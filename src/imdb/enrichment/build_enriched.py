"""Clean, validate and join the raw Wikipedia data with IMDb (Spark).

Inputs: the target tables written by ``select_targets`` and the raw JSON
Lines files written by ``fetch_wikipedia``.

Outputs:
- ``data/enrichment/enriched/films``: one row per (year, genre, rank, film)
  with the synopsis (Parquet, partitioned by year),
- ``data/enrichment/enriched/principals``: one row per (film, principal)
  with the biography (Parquet),
- ``output/enrichment``: coverage, notes and samples for REPORT.md.

Every enriched record carries a ``lineage`` struct (source URLs/URIs,
revision, retrieval time, license) and an ``enrichment_note`` that explains
programmatically why a field is missing.

Usage: python -m imdb.enrichment.build_enriched
"""

import os

from pyspark.sql import Window
from pyspark.sql import functions as F
from pyspark.sql import types as T

from imdb.common import get_spark, write_output
from imdb.enrichment import config as C

LINK_SCHEMA = T.StructType([
    T.StructField("imdb_id", T.StringType()),
    T.StructField("entity_type", T.StringType()),
    T.StructField("wikidata_uri", T.StringType()),
    T.StructField("wikipedia_url", T.StringType()),
    T.StructField("birth_date", T.StringType()),
    T.StructField("death_date", T.StringType()),
    T.StructField("birth_place", T.StringType()),
    T.StructField("source_uri", T.StringType()),
    T.StructField("retrieved_at", T.StringType()),
])

PAGE_SCHEMA = T.StructType([
    T.StructField("imdb_id", T.StringType()),
    T.StructField("entity_type", T.StringType()),
    T.StructField("requested_title", T.StringType()),
    T.StructField("page_id", T.LongType()),
    T.StructField("title", T.StringType()),
    T.StructField("revision_id", T.LongType()),
    T.StructField("page_url", T.StringType()),
    T.StructField("permalink", T.StringType()),
    T.StructField("extract", T.StringType()),
    T.StructField("status", T.StringType()),
    T.StructField("retrieved_at", T.StringType()),
])

# Level-2 headings that hold a film synopsis on English Wikipedia.
PLOT_HEADINGS = ("Plot", "Plot summary", "Synopsis", "Premise", "Story",
                 "Summary", "Storyline")
PLOT_REGEX = (
    r"(?s)(?:^|\n)== (?:" + "|".join(PLOT_HEADINGS) + r") ==\n(.*?)"
    r"(?=\n== [^=]|$)"
)
LEAD_REGEX = r"(?s)^(.*?)(?=\n== [^=]|$)"
MIN_TEXT_LENGTH = 40   # shorter texts are treated as empty


def read_jsonl(spark, paths, schema):
    """Read JSON Lines files with an enforced schema.

    Files that do not exist yet (gathering step not run) are skipped, so the
    job still runs and writes "not fetched yet" notes. Malformed lines (e.g.
    truncated by an interruption) are dropped.
    """
    if isinstance(paths, str):
        paths = [paths]
    existing = [p for p in paths if os.path.exists(p)]
    if not existing:
        return spark.createDataFrame([], schema)
    return (
        spark.read.schema(schema)
        .option("mode", "DROPMALFORMED")
        .json(existing)
        .filter(F.col("imdb_id").isNotNull())
    )


def lineage():
    """Provenance of an enriched record, per source.

    Text fields (synopsis, biography) come from the Wikipedia revision in
    ``source_url`` (CC BY-SA); the article link and, for people, the birth
    and death dates and the birthplace come from the Wikidata item in
    ``wikidata_uri`` (CC0).
    """
    has_page = F.col("permalink").isNotNull()
    has_item = F.col("wikidata_uri").isNotNull()
    return F.struct(
        F.col("permalink").alias("source_url"),
        F.col("page_url").alias("article_url"),
        F.col("revision_id").alias("revision_id"),
        F.col("page_retrieved_at").cast("timestamp")
         .alias("retrieved_at"),
        F.when(has_page, F.lit(C.WIKIPEDIA_LICENSE)).alias("license"),
        F.col("wikidata_uri").alias("wikidata_uri"),
        F.col("link_retrieved_at").cast("timestamp")
         .alias("wikidata_retrieved_at"),
        F.when(has_item, F.lit(C.WIKIDATA_LICENSE))
         .alias("wikidata_license"),
    ).alias("lineage")


def latest_per_id(df, order_col="retrieved_at"):
    """Keep the most recent record of each IMDb ID (re-runs append)."""
    w = Window.partitionBy("imdb_id").orderBy(F.desc(order_col))
    return (df.withColumn("_rn", F.row_number().over(w))
            .filter("_rn = 1").drop("_rn"))


def clean_text(col):
    """Normalise a plain-text extract.

    - remove sub-heading markers (=== Heading ===),
    - remove leftover bracketed reference markers ([1], [note 2], ...),
    - collapse runs of whitespace and trim.
    """
    col = F.regexp_replace(col, r"(?m)^=+ .*? =+\s*$", " ")
    col = F.regexp_replace(col, r"\[(?:\d+|note \d+|[a-z])\]", "")
    col = F.regexp_replace(col, r"\s+", " ")
    col = F.trim(col)
    return F.when(F.length(col) >= MIN_TEXT_LENGTH, col)


def parse_wikidata_date(col):
    """Wikidata dates look like '1946-07-06T00:00:00Z'."""
    return F.to_date(F.substring(col, 1, 10), "yyyy-MM-dd")


def build_films(spark, links, pages):
    targets = spark.read.parquet(C.TARGET_FILMS)
    film_links = links.filter(F.col("entity_type") == "film")
    film_pages = pages.filter(F.col("entity_type") == "film")

    plot = clean_text(F.regexp_extract("extract", PLOT_REGEX, 1))
    lead = clean_text(F.regexp_extract("extract", LEAD_REGEX, 1))
    film_pages = (
        film_pages
        .withColumn("plot", plot)
        .withColumn("lead", lead)
        .select(
            "imdb_id", F.col("title").alias("wikipedia_title"),
            "revision_id", "page_url", "permalink", "plot", "lead",
            "status", F.col("retrieved_at").alias("page_retrieved_at"),
        )
    )

    joined = (
        targets
        .join(film_links.select(
            F.col("imdb_id").alias("tconst"), "wikidata_uri",
            "wikipedia_url", F.col("retrieved_at").alias("link_retrieved_at"),
        ), "tconst", "left")
        .join(film_pages.withColumnRenamed("imdb_id", "tconst"),
              "tconst", "left")
    )

    return joined.select(
        "year", "genre", "rank", "tconst", "primaryTitle",
        "originalTitle", "runtimeMinutes", "averageRating", "numVotes",
        "wikipedia_title",
        F.coalesce("plot", "lead").alias("synopsis"),
        F.when(F.col("plot").isNotNull(), "plot_section")
         .when(F.col("lead").isNotNull(), "lead_section")
         .alias("synopsis_source"),
        lineage(),
        F.when(F.col("wikidata_uri").isNull(),
               "No Wikidata item found for this IMDb ID")
         .when(F.col("wikipedia_url").isNull(),
               "No English Wikipedia article linked to the Wikidata item")
         .when(F.col("status").isNull(),
               "Wikipedia article not fetched yet")
         .when(F.col("status") != "ok",
               "Wikipedia article could not be retrieved")
         .when(F.col("plot").isNull() & F.col("lead").isNotNull(),
               "Article has no plot/synopsis section; lead section used")
         .when(F.col("plot").isNull(),
               "Article has no usable synopsis text")
         .alias("enrichment_note"),
    )


def build_principals(spark, links, pages):
    targets = spark.read.parquet(C.TARGET_PRINCIPALS)
    person_links = links.filter(F.col("entity_type") == "person")
    person_pages = (
        pages.filter(F.col("entity_type") == "person")
        .withColumn("biography", clean_text(F.col("extract")))
        .select(
            F.col("imdb_id").alias("nconst"),
            F.col("title").alias("wikipedia_title"),
            "revision_id", "page_url", "permalink", "biography", "status",
            F.col("retrieved_at").alias("page_retrieved_at"),
        )
    )
    joined = (
        targets
        .join(person_links.select(
            F.col("imdb_id").alias("nconst"), "wikidata_uri",
            "wikipedia_url", "birth_date", "death_date", "birth_place",
            F.col("retrieved_at").alias("link_retrieved_at"),
        ), "nconst", "left")
        .join(person_pages, "nconst", "left")
    )
    return joined.select(
        "tconst", "nconst", "principal_rank", "category", "characters",
        "primaryName", "birthYear", "deathYear",
        parse_wikidata_date("birth_date").alias("birth_date"),
        parse_wikidata_date("death_date").alias("death_date"),
        F.trim("birth_place").alias("birth_place"),
        "wikipedia_title", "biography",
        lineage(),
        F.when(F.col("wikidata_uri").isNull(),
               "No Wikidata item found for this IMDb ID")
         .when(F.col("wikipedia_url").isNull(),
               "No English Wikipedia article linked to the Wikidata item")
         .when(F.col("status").isNull(),
               "Wikipedia article not fetched yet")
         .when(F.col("status") != "ok",
               "Wikipedia article could not be retrieved")
         .when(F.col("biography").isNull(),
               "Article has no usable lead section")
         .alias("enrichment_note"),
    )


def coverage(films, principals):
    film_cov = films.agg(
        F.lit("films (year, genre, rank)").alias("dataset"),
        F.count("*").alias("rows"),
        F.sum(F.col("synopsis").isNotNull().cast("int")).alias("enriched"),
        F.sum((F.col("synopsis_source") == "plot_section").cast("int"))
         .alias("from_plot_section"),
    )
    pr_cov = principals.agg(
        F.lit("principals (film, person)").alias("dataset"),
        F.count("*").alias("rows"),
        F.sum(F.col("biography").isNotNull().cast("int")).alias("enriched"),
        F.lit(None).cast("long").alias("from_plot_section"),
    )
    return (film_cov.unionByName(pr_cov)
            .withColumn("pct_enriched",
                        F.round(100 * F.col("enriched") / F.col("rows"), 1)))


def main():
    spark = get_spark("enrichment-build")
    links = latest_per_id(read_jsonl(spark, C.RAW_LINKS, LINK_SCHEMA))
    pages = latest_per_id(read_jsonl(
        spark, [C.RAW_FILM_PAGES, C.RAW_PERSON_PAGES], PAGE_SCHEMA))

    build_films(spark, links, pages).write.mode("overwrite") \
        .partitionBy("year").parquet(C.ENRICHED_FILMS)
    build_principals(spark, links, pages).write.mode("overwrite") \
        .parquet(C.ENRICHED_PRINCIPALS)
    films = spark.read.parquet(C.ENRICHED_FILMS)
    principals = spark.read.parquet(C.ENRICHED_PRINCIPALS)

    cov = coverage(films, principals)
    write_output(cov, C.SECTION, "coverage")
    cov.show(truncate=False)
    for df, name in ((films, "film_notes"), (principals, "principal_notes")):
        notes = df.groupBy("enrichment_note").count() \
            .orderBy(F.desc("count"))
        write_output(notes, C.SECTION, name)
        notes.show(truncate=False)

    preview = F.concat(F.substring("synopsis", 1, 200), F.lit("..."))
    write_output(
        films.where(F.col("rank") <= 3).orderBy("year", "genre", "rank")
        .select("year", "genre", "rank", "tconst", "primaryTitle",
                "synopsis_source", preview.alias("synopsis_preview"),
                F.col("lineage.source_url").alias("source_url"),
                "enrichment_note"),
        C.SECTION, "films_sample", preview_rows=30)
    bio = F.concat(F.substring("biography", 1, 200), F.lit("..."))
    write_output(
        principals.orderBy(F.desc("tconst"), "principal_rank")
        .select("tconst", "principal_rank", "nconst", "primaryName",
                "category", "birth_date", "birth_place",
                bio.alias("biography_preview"),
                F.col("lineage.source_url").alias("source_url"),
                "enrichment_note"),
        C.SECTION, "principals_sample", preview_rows=30)
    spark.stop()


if __name__ == "__main__":
    main()
