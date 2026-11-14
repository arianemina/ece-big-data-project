"""Q4: directors with exactly one movie rated >= 8.0 who also directed several
other movies rated <= 6.0.

"Several" means at least MIN_LOW_MOVIES movies. Only movies with at least
MIN_VOTES votes are considered so that a rating is backed by enough voters.

Usage: python -m imdb.exploration.q4_directors
"""

import os

from pyspark.sql import functions as F

from imdb.common import get_spark, read_clean, write_output
from imdb.exploration.base import feature_movies, rated, with_names

SECTION = "exploration"
HIGH_RATING = 8.0
LOW_RATING = 6.0
MIN_LOW_MOVIES = 2
MIN_VOTES = int(os.environ.get("Q4_MIN_VOTES", "100"))


def director_movies(spark, min_votes=MIN_VOTES):
    movies = rated(spark, feature_movies(spark), min_votes)
    crew = read_clean(spark, "title_crew").select(
        "tconst", F.explode("directors").alias("nconst"))
    return crew.join(movies, "tconst").select(
        "nconst", "tconst", "primaryTitle", "startYear", "averageRating",
        "numVotes")


def one_hit_directors(spark, min_votes=MIN_VOTES, interpretation="each"):
    """Directors with exactly one movie rated >= 8.0.

    interpretation="each": at least MIN_LOW_MOVIES other movies are each
    rated <= 6.0. interpretation="average": at least MIN_LOW_MOVIES other
    movies whose average rating, taken together, is <= 6.0.
    """
    films = director_movies(spark, min_votes)
    high = F.col("averageRating") >= HIGH_RATING
    low = F.col("averageRating") <= LOW_RATING
    per_director = films.groupBy("nconst").agg(
        F.sum(F.when(high, 1).otherwise(0)).alias("movies_rated_8_plus"),
        F.sum(F.when(low, 1).otherwise(0)).alias("movies_rated_6_or_less"),
        F.count("*").alias("rated_movies"),
        F.max(F.when(high, F.struct("averageRating", "primaryTitle",
                                    "startYear"))).alias("hit"),
        F.round(F.avg(F.when(low, F.col("averageRating"))), 2)
        .alias("avg_rating_of_low_movies"),
        F.round(F.avg(F.when(~high, F.col("averageRating"))), 2)
        .alias("avg_rating_of_other_movies"),
    ).withColumn("other_movies", F.col("rated_movies") - 1)
    if interpretation == "each":
        condition = F.col("movies_rated_6_or_less") >= MIN_LOW_MOVIES
    elif interpretation == "average":
        condition = ((F.col("other_movies") >= MIN_LOW_MOVIES)
                     & (F.col("avg_rating_of_other_movies") <= LOW_RATING))
    else:
        raise ValueError(f"unknown interpretation {interpretation}")
    result = per_director.where(
        (F.col("movies_rated_8_plus") == 1) & condition
    ).select(
        "nconst",
        F.col("hit.primaryTitle").alias("hit_title"),
        F.col("hit.startYear").alias("hit_year"),
        F.col("hit.averageRating").alias("hit_rating"),
        "movies_rated_6_or_less", "avg_rating_of_low_movies",
        "other_movies", "avg_rating_of_other_movies", "rated_movies",
    )
    return with_names(spark, result).select(
        "nconst", "primaryName", "hit_title", "hit_year", "hit_rating",
        "movies_rated_6_or_less", "avg_rating_of_low_movies",
        "other_movies", "avg_rating_of_other_movies", "rated_movies")


def main():
    spark = get_spark("imdb-q4")
    result = one_hit_directors(spark).orderBy(
        F.desc("movies_rated_6_or_less"), "primaryName")
    total = write_output(result, SECTION, "q4_one_hit_directors")
    print(f"{total} directors found (each other movie rated <= 6.0)")
    average = one_hit_directors(spark, interpretation="average").orderBy(
        F.desc("other_movies"), "primaryName")
    n_avg = write_output(average, SECTION, "q4_one_hit_directors_average")
    print(f"{n_avg} directors found (other movies average <= 6.0)")
    result.show(30, truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
