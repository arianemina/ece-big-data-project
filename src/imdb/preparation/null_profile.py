"""Percentage of null, missing or empty values for every column of IMDb.

A value counts as missing when it is a real null, the IMDb marker "\\N", or a
string that is empty after trimming whitespace.

Usage: python -m imdb.preparation.null_profile
"""

from pyspark.sql import functions as F

from imdb.common import (RAW_TABLES, get_spark, is_missing, read_raw,
                         write_output)

SECTION = "preparation"


def profile_table(spark, table, raw_dir=None):
    """Return one row per column with missing counts and percentage."""
    df = read_raw(spark, table, raw_dir)
    aggregations = [F.count(F.lit(1)).alias("__total")]
    aggregations += [
        F.sum(F.when(is_missing(c), 1).otherwise(0)).alias(c)
        for c in df.columns
    ]
    counts = df.agg(*aggregations).collect()[0].asDict()
    total = counts.pop("__total")
    rows = []
    for column in df.columns:
        missing = counts[column] or 0
        pct = 100.0 * missing / total if total else 0.0
        rows.append((table, column, total, missing, round(pct, 4)))
    return rows


def profile_all(spark, raw_dir=None):
    """Profile every IMDb table and return a single DataFrame."""
    rows = []
    for table in RAW_TABLES:
        rows.extend(profile_table(spark, table, raw_dir))
    return spark.createDataFrame(
        rows,
        "table STRING, column STRING, total_rows LONG, "
        "missing_rows LONG, missing_pct DOUBLE",
    )


def main():
    spark = get_spark("imdb-null-profile")
    profile = profile_all(spark).cache()
    write_output(profile.orderBy("table", "column"), SECTION,
                 "null_profile", preview_rows=100)
    top5 = profile.orderBy(F.desc("missing_pct"), "table", "column").limit(5)
    write_output(top5, SECTION, "null_profile_top5")
    top5.show(truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
