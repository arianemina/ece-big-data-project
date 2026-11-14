"""Q1: feature-length movies whose length is notably different from the
average length of movies in the same genre.

Runtimes are strongly right-skewed (a few experimental films last several
days), so a plain mean / standard deviation z-score only flags extremely
long films. The score used here is the robust (modified) z-score of
Iglewicz and Hoaglin computed on log(runtime):

    robust_z = 0.6745 * (log(runtime) - median) / MAD

where median and MAD (median absolute deviation) are taken per genre on
log(runtime). A movie is an outlier when |robust_z| >= Z_THRESHOLD (3.5 by
default). The log makes "twice as long" and "half as long" symmetric, so
unusually short feature films are detected as well as long ones. The plain
mean / standard deviation statistics are still reported per genre.

Usage: python -m imdb.exploration.q1_runtime_outliers
"""

import os

from pyspark.sql import functions as F

from imdb.common import get_spark, write_output
from imdb.exploration.base import by_genre, feature_movies

SECTION = "exploration"
Z_THRESHOLD = float(os.environ.get("Q1_Z_THRESHOLD", "3.5"))
MAD_SCALE = 0.6745
MEANAD_SCALE = 1.253314


def genre_stats(movies):
    return by_genre(movies).groupBy("genre").agg(
        F.count("*").alias("movies"),
        F.round(F.avg("runtimeMinutes"), 2).alias("avg_runtime"),
        F.round(F.stddev_pop("runtimeMinutes"), 2).alias("std_runtime"),
        F.expr("percentile_approx(runtimeMinutes, 0.5)")
        .alias("median_runtime"),
    )


def runtime_outliers(movies, z_threshold=Z_THRESHOLD):
    rows = by_genre(movies).withColumn("log_runtime",
                                       F.log(F.col("runtimeMinutes")))
    medians = rows.groupBy("genre").agg(
        F.percentile("log_runtime", 0.5).alias("log_median"),
        F.percentile("runtimeMinutes", 0.5).alias("median_runtime"))
    with_dev = rows.join(medians, "genre").withColumn(
        "abs_dev", F.abs(F.col("log_runtime") - F.col("log_median")))
    mads = with_dev.groupBy("genre").agg(
        F.percentile("abs_dev", 0.5).alias("log_mad"),
        F.avg("abs_dev").alias("log_meanad"))
    deviation = F.col("log_runtime") - F.col("log_median")
    scored = with_dev.join(mads, "genre").withColumn(
        "robust_z",
        # When more than half of a genre shares the median runtime the MAD
        # is 0; the mean absolute deviation is then used instead
        # (IBM SPSS / Iglewicz-Hoaglin convention).
        F.when(F.col("log_mad") > 0,
               MAD_SCALE * deviation / F.col("log_mad"))
        .otherwise(F.try_divide(deviation,
                                MEANAD_SCALE * F.col("log_meanad"))))
    return (
        scored.where(F.abs("robust_z") >= z_threshold)
        .withColumn("direction",
                    F.when(F.col("robust_z") > 0, "longer")
                    .otherwise("shorter"))
        .select("genre", "tconst", "primaryTitle", "startYear",
                "runtimeMinutes",
                F.round("median_runtime", 1).alias("genre_median_runtime"),
                F.round("robust_z", 2).alias("robust_z"), "direction")
    )


def main():
    spark = get_spark("imdb-q1")
    movies = feature_movies(spark).cache()
    stats = genre_stats(movies).orderBy("genre")
    outliers = runtime_outliers(movies).cache()
    write_output(stats, SECTION, "q1_genre_runtime_stats", preview_rows=40)
    write_output(outliers.orderBy(F.desc(F.abs("robust_z"))), SECTION,
                 "q1_runtime_outliers")
    summary = outliers.groupBy("genre").agg(
        F.count("*").alias("outliers"),
        F.sum(F.when(F.col("direction") == "longer", 1).otherwise(0))
        .alias("longer"),
        F.sum(F.when(F.col("direction") == "shorter", 1).otherwise(0))
        .alias("shorter"),
    ).join(stats.select("genre", "movies"), "genre") \
        .withColumn("outlier_pct",
                    F.round(100 * F.col("outliers") / F.col("movies"), 2)) \
        .orderBy("genre")
    write_output(summary, SECTION, "q1_outliers_by_genre", preview_rows=40)
    summary.show(40, truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
