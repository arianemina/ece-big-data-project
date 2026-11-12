"""Apply the data quality rules and write cleaned Parquet tables.

Rules (one function per table):
- duplicated primary keys are removed (first occurrence kept);
- impossible values are set to null and flagged in a dq_* column, so that the
  row stays usable for the other columns;
- relation rows whose foreign key has no parent are removed, and list
  columns only keep ids that exist in the parent table;
- ratings outside the IMDb scale are removed.

Usage: python -m imdb.preparation.clean
"""

import os

from pyspark.sql import functions as F

from imdb.common import CLEAN_DIR, get_spark, write_output
from imdb.preparation.quality_checks import MAX_LIFESPAN, REFERENCE_YEAR
from imdb.preparation.schema import typed_tables

SECTION = "preparation"


def clean_names(names):
    names = names.where(F.col("nconst").isNotNull()).dropDuplicates(["nconst"])
    flagged = (
        names
        .withColumn("_future_birth", F.col("birthYear") > REFERENCE_YEAR)
        .withColumn("_future_death", F.col("deathYear") > REFERENCE_YEAR)
        .withColumn("_impossible",
                    (F.col("deathYear") < F.col("birthYear"))
                    | (F.col("deathYear") - F.col("birthYear")
                       > MAX_LIFESPAN))
    )
    impossible = F.coalesce(F.col("_impossible"), F.lit(False))
    future_birth = F.coalesce(F.col("_future_birth"), F.lit(False))
    future_death = F.coalesce(F.col("_future_death"), F.lit(False))
    return (
        flagged
        .withColumn("dq_invalid_lifespan",
                    impossible | future_birth | future_death)
        # We cannot know which of the two years is wrong, so both are nulled
        # when the lifespan is impossible; a single year in the future is
        # nulled on its own.
        .withColumn("birthYear",
                    F.when(impossible | future_birth, None)
                    .otherwise(F.col("birthYear")))
        .withColumn("deathYear",
                    F.when(impossible | future_death, None)
                    .otherwise(F.col("deathYear")))
        .drop("_future_birth", "_future_death", "_impossible")
    )


def clean_basics(basics):
    basics = basics.where(F.col("tconst").isNotNull()) \
        .dropDuplicates(["tconst"])
    return (
        basics
        .withColumn("isAdult",
                    F.when(F.col("isAdult").isin(0, 1), F.col("isAdult")))
        .withColumn("dq_end_before_start",
                    F.coalesce(F.col("endYear") < F.col("startYear"),
                               F.lit(False)))
        .withColumn("endYear",
                    F.when(F.col("dq_end_before_start"), None)
                    .otherwise(F.col("endYear")))
        .withColumn("runtimeMinutes",
                    F.when(F.col("runtimeMinutes") > 0,
                           F.col("runtimeMinutes")))
        .withColumn("is_upcoming",
                    F.coalesce(F.col("startYear") > REFERENCE_YEAR,
                               F.lit(False)))
    )


def _keep_existing(df, key, parent_keys):
    return df.join(parent_keys, on=key, how="left_semi")


def _filter_id_array(df, row_key, array_col, parent_keys, parent_key):
    """Keep only array elements that exist in parent_keys (order kept)."""
    exploded = df.select(row_key, F.posexplode(array_col).alias("pos", "id"))
    valid = exploded.join(
        parent_keys.withColumnRenamed(parent_key, "id"), "id", "left_semi")
    rebuilt = valid.groupBy(row_key).agg(
        F.array_sort(F.collect_list(F.struct("pos", "id"))).alias("_items"))
    rebuilt = rebuilt.select(row_key,
                             F.col("_items.id").alias(array_col))
    return df.drop(array_col).join(rebuilt, row_key, "left")


def clean_all(tables):
    """Return a dict of cleaned DataFrames."""
    names = clean_names(tables["name.basics"])
    basics = clean_basics(tables["title.basics"])
    title_keys = basics.select("tconst")
    name_keys = names.select("nconst")

    names = _filter_id_array(names, "nconst", "knownForTitles",
                             title_keys, "tconst")

    akas = tables["title.akas"].withColumnRenamed("titleId", "tconst")
    akas = _keep_existing(akas, "tconst", title_keys) \
        .dropDuplicates(["tconst", "ordering"])

    crew = _keep_existing(tables["title.crew"], "tconst", title_keys) \
        .dropDuplicates(["tconst"])
    crew = _filter_id_array(crew, "tconst", "directors", name_keys, "nconst")
    crew = _filter_id_array(crew, "tconst", "writers", name_keys, "nconst")

    episode = tables["title.episode"].dropDuplicates(["tconst"])
    episode = _keep_existing(episode, "tconst", title_keys)
    episode = _keep_existing(
        episode, "parentTconst",
        title_keys.withColumnRenamed("tconst", "parentTconst"))

    principals = tables["title.principals"] \
        .dropDuplicates(["tconst", "ordering"])
    principals = _keep_existing(principals, "tconst", title_keys)
    principals = _keep_existing(principals, "nconst", name_keys)
    principals = _flag_credit_dates(principals, basics, names)

    ratings = tables["title.ratings"].dropDuplicates(["tconst"])
    ratings = _keep_existing(ratings, "tconst", title_keys).where(
        F.col("averageRating").between(1.0, 10.0) & (F.col("numVotes") >= 1))

    return {
        "name_basics": names,
        "title_basics": basics,
        "title_akas": akas,
        "title_crew": crew,
        "title_episode": episode,
        "title_principals": principals,
        "title_ratings": ratings,
    }


def _flag_credit_dates(principals, basics, names):
    """Flag credits dated before the person's birth (kept, not removed)."""
    years = basics.select("tconst", "startYear")
    births = names.select("nconst", "birthYear")
    return (
        principals.join(years, "tconst", "left")
        .join(births, "nconst", "left")
        .withColumn("dq_credit_before_birth",
                    F.coalesce(F.col("startYear") < F.col("birthYear"),
                               F.lit(False)))
        .drop("startYear", "birthYear")
    )


def main():
    spark = get_spark("imdb-clean")
    raw = typed_tables(spark)
    raw_counts = {name: df.count() for name, df in raw.items()}
    cleaned = clean_all(raw)
    report = []
    for name, df in cleaned.items():
        path = os.path.join(CLEAN_DIR, name)
        df.write.mode("overwrite").parquet(path)
        kept = spark.read.parquet(path).count()
        before = raw_counts[name.replace("_", ".", 1)]
        report.append((name, before, kept, before - kept))
    summary = spark.createDataFrame(
        report, "table STRING, raw_rows LONG, clean_rows LONG, "
                "removed_rows LONG")
    write_output(summary, SECTION, "clean_summary")
    summary.show(truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
