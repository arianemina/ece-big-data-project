"""Q7: actors and actresses with a career of 20+ years and 15+ movies whose
popularity peaked early in their career.

Career = years between their first and last rated feature-length movie. The
career is split in two halves at its middle year. An actor peaked early when
their highest rated movie is in the first half AND the average rating of the
first half is higher than that of the second half.

Usage: python -m imdb.exploration.q7_early_peak
"""

import os

from pyspark.sql import Window
from pyspark.sql import functions as F

from imdb.common import get_spark, write_output
from imdb.exploration.base import (actor_credits, feature_movies, rated,
                                   with_names)

SECTION = "exploration"
MIN_CAREER_YEARS = 20
MIN_MOVIES = 15
MIN_VOTES = int(os.environ.get("Q7_MIN_VOTES", "100"))


def early_peak_actors(spark, min_votes=MIN_VOTES):
    movies = rated(spark, feature_movies(spark), min_votes) \
        .where(F.col("startYear").isNotNull()) \
        .select("tconst", "primaryTitle", "startYear", "averageRating",
                "numVotes")
    credits = actor_credits(spark).join(movies, "tconst")

    per = Window.partitionBy("nconst")
    best = Window.partitionBy("nconst").orderBy(
        F.desc("averageRating"), F.desc("numVotes"))
    credits = (
        credits
        .withColumn("first_year", F.min("startYear").over(per))
        .withColumn("last_year", F.max("startYear").over(per))
        .withColumn("mid_year",
                    (F.col("first_year") + F.col("last_year")) / 2)
        .withColumn("is_early", F.col("startYear") <= F.col("mid_year"))
        .withColumn("best_rank", F.row_number().over(best))
    )
    per_actor = credits.groupBy("nconst").agg(
        F.first("first_year").alias("first_year"),
        F.first("last_year").alias("last_year"),
        F.count("*").alias("movies"),
        F.round(F.avg(F.when(F.col("is_early"), F.col("averageRating"))), 2)
        .alias("early_avg_rating"),
        F.round(F.avg(F.when(~F.col("is_early"), F.col("averageRating"))), 2)
        .alias("late_avg_rating"),
        F.max(F.when(F.col("best_rank") == 1,
                     F.struct("primaryTitle", "startYear", "averageRating",
                              "is_early"))).alias("best"),
    ).withColumn("career_years", F.col("last_year") - F.col("first_year"))

    result = per_actor.where(
        (F.col("career_years") >= MIN_CAREER_YEARS)
        & (F.col("movies") >= MIN_MOVIES)
        & F.col("best.is_early")
        & (F.col("early_avg_rating") > F.col("late_avg_rating"))
    ).select(
        "nconst", "first_year", "last_year", "career_years", "movies",
        F.col("best.primaryTitle").alias("best_movie"),
        F.col("best.startYear").alias("best_year"),
        F.col("best.averageRating").alias("best_rating"),
        "early_avg_rating", "late_avg_rating",
        F.round(F.col("early_avg_rating") - F.col("late_avg_rating"), 2)
        .alias("rating_drop"),
    )
    return with_names(spark, result)


def main():
    spark = get_spark("imdb-q7")
    result = early_peak_actors(spark).orderBy(F.desc("rating_drop"))
    total = write_output(result.select(
        "nconst", "primaryName", "first_year", "last_year", "career_years",
        "movies", "best_movie", "best_year", "best_rating",
        "early_avg_rating", "late_avg_rating", "rating_drop"),
        SECTION, "q7_early_peak_actors")
    print(f"{total} actors found")
    result.show(30, truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
