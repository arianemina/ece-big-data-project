"""Build the static lookup table used to filter the Wikipedia stream (Spark).

Built from the cleaned IMDb tables (run the preparation step first).

A Wikipedia change event only carries the page title, so the stream is
matched on a normalised (lower-case) page title. The reference table maps
candidate Wikipedia titles to IMDb entities:

1. ``enriched_article``: exact titles of the Wikipedia articles collected by
   the enrichment pipeline (most precise, used when available);
2. ``imdb_title``: movies and TV series with at least ``--min-votes`` votes,
   as "Title", "Title (film)", "Title (YYYY film)", "Title (TV series)",
   "Title (YYYY TV series)", "Title (miniseries)";
3. ``imdb_person``: principals (cast and crew) of those titles, as "Name"
   and "Name (<job>)" for the jobs they held, e.g. "Name (actor)",
   "Name (director)", "Name (filmmaker)", "Name (screenwriter)".

When several IMDb entities share a key, the most popular one is kept and
the number of candidates is recorded (``n_candidates``).

Usage:
    python -m imdb.streaming.build_reference [--min-votes 5000]
"""
import argparse
import os

from pyspark.sql import Window
from pyspark.sql import functions as F

from imdb.common import get_spark, read_clean
from imdb.streaming import config as C

FILM_TYPES = ["movie", "tvMovie"]
SERIES_TYPES = ["tvSeries", "tvMiniSeries"]
# IMDb category -> disambiguation suffixes used by Wikipedia article titles
PERSON_SUFFIXES = {
    "actor": ["actor"],
    "actress": ["actress", "actor"],
    "director": ["director", "filmmaker"],
    "writer": ["writer", "screenwriter"],
    "producer": ["producer"],
    "composer": ["composer", "musician"],
}
PRIORITY = {"enriched_article": 0, "imdb_title": 1, "imdb_person": 2}


def key(col):
    return F.lower(F.trim(col))


def explode_keys(variants):
    """One normalised match key per (non-null) variant."""
    return F.explode(F.array_distinct(F.filter(
        F.transform(variants, key), lambda k: k.isNotNull())))


def title_keys(basics, ratings, min_votes):
    titles = (
        basics.filter(F.col("titleType").isin(FILM_TYPES + SERIES_TYPES))
        .join(ratings.filter(F.col("numVotes") >= min_votes), "tconst")
    )
    year = F.col("startYear").cast("string")
    is_film = F.col("titleType").isin(FILM_TYPES)
    # A one-word title ("Up", "Heat", "Chicago") usually names another
    # article: keep the bare form only for titles of two words or more and
    # rely on the disambiguated forms ("Heat (1995 film)") otherwise.
    bare = F.when(F.col("primaryTitle").contains(" "), F.col("primaryTitle"))
    variants = F.when(
        is_film,
        F.array(
            bare,
            F.concat_ws("", "primaryTitle", F.lit(" (film)")),
            F.concat_ws("", "primaryTitle", F.lit(" ("), year,
                        F.lit(" film)")),
        ),
    ).otherwise(
        F.array(
            bare,
            F.concat_ws("", "primaryTitle", F.lit(" (TV series)")),
            F.concat_ws("", "primaryTitle", F.lit(" ("), year,
                        F.lit(" TV series)")),
            F.concat_ws("", "primaryTitle", F.lit(" (miniseries)")),
        )
    )
    return titles.select(
        explode_keys(variants).alias("match_key"),
        F.when(is_film, "film").otherwise("series").alias("entity_type"),
        F.col("tconst").alias("imdb_id"),
        F.col("primaryTitle").alias("imdb_name"),
        F.col("numVotes").alias("popularity"),
        F.lit("imdb_title").alias("match_type"),
    ), titles


def person_keys(principals, names, titles):
    """Name keys of the cast and crew of the reference titles.

    Each person gets the bare name plus the disambiguation suffixes that
    match the jobs they actually held (e.g. "(actress)" only for actresses)
    to keep the lookup table small.
    """
    suffix_map = F.create_map(*[x for cat, sfx in PERSON_SUFFIXES.items()
                                for x in (F.lit(cat), F.array(
                                    *[F.lit(v) for v in sfx]))])
    credits = (
        principals.filter(F.col("category").isin(list(PERSON_SUFFIXES)))
        .join(titles.select("tconst", "numVotes"), "tconst")
    )
    people = (
        credits.groupBy("nconst").agg(
            F.sum("numVotes").cast("long").alias("popularity"),
            F.array_distinct(F.flatten(F.collect_set(
                suffix_map[F.col("category")]))).alias("suffixes"))
        .join(names.select("nconst", "primaryName"), "nconst")
    )
    variants = F.concat(
        F.array(F.col("primaryName")),
        F.transform("suffixes", lambda sfx: F.concat_ws(
            "", F.col("primaryName"), F.lit(" ("), sfx, F.lit(")"))),
    )
    return people.select(
        explode_keys(variants).alias("match_key"),
        F.lit("person").alias("entity_type"),
        F.col("nconst").alias("imdb_id"),
        F.col("primaryName").alias("imdb_name"),
        "popularity",
        F.lit("imdb_person").alias("match_type"),
    )


def enriched_keys(spark):
    """Exact article titles found by the enrichment pipeline, if present."""
    parts = []
    if os.path.exists(C.ENRICHED_FILMS):
        parts.append(
            spark.read.parquet(C.ENRICHED_FILMS)
            .filter(F.col("wikipedia_title").isNotNull())
            .select(key("wikipedia_title").alias("match_key"),
                    F.lit("film").alias("entity_type"),
                    F.col("tconst").alias("imdb_id"),
                    F.col("primaryTitle").alias("imdb_name"),
                    F.col("numVotes").cast("long").alias("popularity"),
                    F.lit("enriched_article").alias("match_type"))
        )
    if os.path.exists(C.ENRICHED_PRINCIPALS):
        parts.append(
            spark.read.parquet(C.ENRICHED_PRINCIPALS)
            .filter(F.col("wikipedia_title").isNotNull())
            .select(key("wikipedia_title").alias("match_key"),
                    F.lit("person").alias("entity_type"),
                    F.col("nconst").alias("imdb_id"),
                    F.col("primaryName").alias("imdb_name"),
                    F.lit(None).cast("long").alias("popularity"),
                    F.lit("enriched_article").alias("match_type"))
        )
    return parts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-votes", type=int, default=C.MIN_VOTES)
    args = parser.parse_args()

    spark = get_spark("streaming-build-reference")
    basics = read_clean(spark, "title_basics")
    ratings = read_clean(spark, "title_ratings")
    principals = read_clean(spark, "title_principals")
    names = read_clean(spark, "name_basics")

    t_keys, titles = title_keys(basics, ratings, args.min_votes)
    p_keys = person_keys(principals, names, titles)
    candidates = (
        t_keys.withColumn("popularity", F.col("popularity").cast("long"))
        .unionByName(p_keys)
    )
    for part in enriched_keys(spark):
        candidates = candidates.unionByName(part)

    priority = F.create_map(*[x for k, v in PRIORITY.items()
                              for x in (F.lit(k), F.lit(v))])
    w_rank = Window.partitionBy("match_key").orderBy(
        priority[F.col("match_type")], F.desc_nulls_last("popularity"),
        "imdb_id")
    w_all = Window.partitionBy("match_key")
    reference = (
        candidates.dropDuplicates(["match_key", "imdb_id"])
        # True when the page title is the bare IMDb name (no "(film)", ...)
        .withColumn("bare_key", F.col("match_key") == key("imdb_name"))
        .filter(F.length("match_key") >= 3)
        .withColumn("n_candidates", F.count("*").over(w_all))
        .withColumn("_rn", F.row_number().over(w_rank))
        .filter("_rn = 1").drop("_rn")
    )
    reference.coalesce(1).write.mode("overwrite").parquet(C.REFERENCE)
    reference = spark.read.parquet(C.REFERENCE)
    print(f"reference keys: {reference.count():,}")
    reference.groupBy("match_type", "entity_type").count() \
        .orderBy("match_type", "entity_type").show()
    spark.stop()


if __name__ == "__main__":
    main()
