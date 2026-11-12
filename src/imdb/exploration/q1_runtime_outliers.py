"""Q1: feature-length movies whose length is notably different from the
average length of movies in the same genre.

A movie is an outlier for a genre when its runtime is more than Z_THRESHOLD
standard deviations away from the genre mean (|z-score| >= Z_THRESHOLD).

Usage: python -m imdb.exploration.q1_runtime_outliers
"""

import os

from pyspark.sql import Window
from pyspark.sql import functions as F

from imdb.common import get_spark, write_output
from imdb.exploration.base import by_genre, feature_movies

SECTION = "exploration"
Z_THRESHOLD = float(os.environ.get("Q1_Z_THRESHOLD", "3"))


def genre_stats(movies):
    return by_genre(movies).groupBy("genre").agg(
        F.count("*").alias("movies"),
        F.round(F.avg("runtimeMinutes"), 2).alias("avg_runtime"),
        F.round(F.stddev_pop("runtimeMinutes"), 2).alias("std_runtime"),
        F.expr("percentile_approx(runtimeMinutes, 0.5)")
        .alias("median_runtime"),
    )


def runtime_outliers(movies, z_threshold=Z_THRESHOLD):
    per_genre = Window.partitionBy("genre")
    scored = (
        by_genre(movies)
        .withColumn("avg_runtime", F.avg("runtimeMinutes").over(per_genre))
        .withColumn("std_runtime",
                    F.stddev_pop("runtimeMinutes").over(per_genre))
        .withColumn("z_score",
                    F.try_divide(F.col("runtimeMinutes")
                                 - F.col("avg_runtime"),
                                 F.col("std_runtime")))
    )
    return (
        scored.where(F.abs("z_score") >= z_threshold)
        .withColumn("direction",
                    F.when(F.col("z_score") > 0, "longer")
                    .otherwise("shorter"))
        .select("genre", "tconst", "primaryTitle", "startYear",
                "runtimeMinutes", F.round("avg_runtime", 2)
                .alias("genre_avg_runtime"),
                F.round("std_runtime", 2).alias("genre_std_runtime"),
                F.round("z_score", 2).alias("z_score"), "direction")
    )


def main():
    spark = get_spark("imdb-q1")
    movies = feature_movies(spark).cache()
    stats = genre_stats(movies).orderBy("genre")
    outliers = runtime_outliers(movies).cache()
    write_output(stats, SECTION, "q1_genre_runtime_stats", preview_rows=40)
    write_output(outliers.orderBy(F.desc(F.abs("z_score"))), SECTION,
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
