"""Q5: TV series with at least three seasons of 10 or more episodes, whose
worst episode is in the last season and best episode in the first two seasons.

Seasons are counted from title.episode (all episodes, rated or not). Worst and
best episodes are taken among episodes with at least MIN_VOTES votes. When
several episodes share the best (or worst) rating, every one of them must sit
in the required seasons.

Usage: python -m imdb.exploration.q5_tv_series
"""

import os

from pyspark.sql import Window
from pyspark.sql import functions as F

from imdb.common import get_spark, read_clean, write_output

SECTION = "exploration"
MIN_SEASONS = 3
MIN_EPISODES = 10
MIN_VOTES = int(os.environ.get("Q5_MIN_VOTES", "20"))


def qualifying_series(spark, min_votes=MIN_VOTES):
    basics = read_clean(spark, "title_basics")
    series = basics.where(F.col("titleType") == "tvSeries").select(
        F.col("tconst").alias("parentTconst"),
        F.col("primaryTitle").alias("series_title"),
        F.col("startYear").alias("series_start"))
    episodes = read_clean(spark, "title_episode") \
        .where(F.col("seasonNumber").isNotNull()) \
        .join(series, "parentTconst")

    season_sizes = episodes.groupBy("parentTconst", "seasonNumber") \
        .agg(F.count("*").alias("episodes"))
    per_series = season_sizes.groupBy("parentTconst").agg(
        F.sum(F.when(F.col("episodes") >= MIN_EPISODES, 1).otherwise(0))
        .alias("big_seasons"),
        F.max("seasonNumber").alias("last_season"),
        F.count("*").alias("seasons"),
    ).where(F.col("big_seasons") >= MIN_SEASONS)

    ratings = read_clean(spark, "title_ratings") \
        .where(F.col("numVotes") >= min_votes)
    rated_eps = episodes.join(per_series, "parentTconst") \
        .join(ratings, "tconst")

    # The first two seasons are the two lowest season numbers of the series.
    season_rank = Window.partitionBy("parentTconst").orderBy("seasonNumber")
    season_pos = season_sizes.select("parentTconst", "seasonNumber") \
        .withColumn("season_pos", F.row_number().over(season_rank))
    rated_eps = rated_eps.join(season_pos, ["parentTconst", "seasonNumber"])

    per = Window.partitionBy("parentTconst")
    rated_eps = (
        rated_eps
        .withColumn("min_rating", F.min("averageRating").over(per))
        .withColumn("max_rating", F.max("averageRating").over(per))
    )
    worst = rated_eps.where(F.col("averageRating") == F.col("min_rating"))
    best = rated_eps.where(F.col("averageRating") == F.col("max_rating"))

    worst_ok = worst.groupBy("parentTconst").agg(
        F.min(F.col("seasonNumber") == F.col("last_season")).alias("ok"),
        F.first("tconst").alias("worst_episode"),
        F.first("seasonNumber").alias("worst_season"),
        F.first("averageRating").alias("worst_rating"),
    ).where("ok").drop("ok")
    best_ok = best.groupBy("parentTconst").agg(
        F.min(F.col("season_pos") <= 2).alias("ok"),
        F.first("tconst").alias("best_episode"),
        F.first("seasonNumber").alias("best_season"),
        F.first("averageRating").alias("best_rating"),
    ).where("ok").drop("ok")

    return (
        worst_ok.join(best_ok, "parentTconst")
        .join(per_series, "parentTconst")
        .join(series, "parentTconst")
        .select(F.col("parentTconst").alias("series_tconst"),
                "series_title", "series_start", "seasons", "big_seasons",
                "last_season", "best_episode", "best_season", "best_rating",
                "worst_episode", "worst_season", "worst_rating")
    )


def main():
    spark = get_spark("imdb-q5")
    result = qualifying_series(spark).orderBy("series_title")
    total = write_output(result, SECTION, "q5_tv_series")
    print(f"{total} series found")
    result.show(30, truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
