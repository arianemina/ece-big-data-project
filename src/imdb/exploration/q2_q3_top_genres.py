"""Q2: top three most popular movie genres for each year 1980-2025.
Q3: how the top three genres compare to the rest of the genres each year.

Popularity of a genre in a year = total number of IMDb votes received by the
feature-length movies of that genre released that year. The number of movies
and the average rating are kept to compare the top three with the others.

Usage: python -m imdb.exploration.q2_q3_top_genres
"""

import os

from pyspark.sql import Window
from pyspark.sql import functions as F

from imdb.common import get_spark, write_output
from imdb.exploration.base import by_genre, feature_movies, rated

SECTION = "exploration"
FIRST_YEAR = int(os.environ.get("FIRST_YEAR", "1980"))
LAST_YEAR = int(os.environ.get("LAST_YEAR", "2025"))
TOP_N = 3


def genre_year_popularity(spark, movies, first_year=FIRST_YEAR,
                          last_year=LAST_YEAR):
    in_range = movies.where(
        F.col("startYear").between(first_year, last_year))
    rated_genres = by_genre(rated(spark, in_range))
    stats = rated_genres.groupBy("startYear", "genre").agg(
        F.sum("numVotes").alias("total_votes"),
        F.count("*").alias("movies"),
        # Votes weighted mean, so that heavily watched movies count more.
        F.round(F.sum(F.col("averageRating") * F.col("numVotes"))
                / F.sum("numVotes"), 3).alias("weighted_rating"),
        F.round(F.avg("averageRating"), 3).alias("avg_rating"),
    )
    rank = Window.partitionBy("startYear").orderBy(
        F.desc("total_votes"), F.desc("movies"), "genre")
    return stats.withColumn("rank", F.row_number().over(rank)) \
        .withColumnRenamed("startYear", "year")


def top_genres(popularity, top_n=TOP_N):
    return popularity.where(F.col("rank") <= top_n) \
        .orderBy("year", "rank")


def top_vs_rest(popularity, top_n=TOP_N):
    grouped = popularity.withColumn(
        "group", F.when(F.col("rank") <= top_n, "top3").otherwise("rest"))
    year_totals = popularity.groupBy("year").agg(
        F.sum("total_votes").alias("year_votes"),
        F.sum("movies").alias("year_genre_movies"))
    per_group = grouped.groupBy("year", "group").agg(
        F.count("*").alias("genres"),
        F.sum("total_votes").alias("votes"),
        F.sum("movies").alias("movies"),
        F.round(F.sum(F.col("weighted_rating") * F.col("total_votes"))
                / F.sum("total_votes"), 3).alias("weighted_rating"),
    )
    pivot = per_group.groupBy("year").pivot("group", ["top3", "rest"]).agg(
        F.first("genres").alias("genres"),
        F.first("votes").alias("votes"),
        F.first("movies").alias("movies"),
        F.first("weighted_rating").alias("rating"),
    )
    return (
        pivot.join(year_totals, "year")
        .withColumn("top3_vote_share_pct",
                    F.round(100 * F.col("top3_votes") / F.col("year_votes"),
                            2))
        .withColumn("top3_movie_share_pct",
                    F.round(100 * F.col("top3_movies")
                            / F.col("year_genre_movies"), 2))
        .withColumn("top3_votes_per_movie",
                    F.round(F.col("top3_votes") / F.col("top3_movies"), 0))
        .withColumn("rest_votes_per_movie",
                    F.round(F.col("rest_votes") / F.col("rest_movies"), 0))
        .select("year", "top3_genres", "rest_genres", "top3_vote_share_pct",
                "top3_movie_share_pct", "top3_votes_per_movie",
                "rest_votes_per_movie", "top3_rating", "rest_rating")
        .orderBy("year")
    )


def main():
    spark = get_spark("imdb-q2-q3")
    popularity = genre_year_popularity(spark, feature_movies(spark)).cache()
    top = top_genres(popularity)
    write_output(top.select("year", "rank", "genre", "total_votes", "movies",
                            "weighted_rating"),
                 SECTION, "q2_top3_genres_per_year", preview_rows=200)
    wide = top.groupBy("year").agg(
        F.concat_ws(", ", F.transform(
            F.array_sort(F.collect_list(F.struct("rank", "genre"))),
            lambda s: s["genre"])).alias("top3_genres")).orderBy("year")
    write_output(wide, SECTION, "q2_top3_genres_compact", preview_rows=60)
    comparison = top_vs_rest(popularity)
    write_output(comparison, SECTION, "q3_top3_vs_rest", preview_rows=60)
    frequency = top.groupBy("genre").agg(
        F.count("*").alias("years_in_top3"),
        F.sum(F.when(F.col("rank") == 1, 1).otherwise(0))
        .alias("years_ranked_first")).orderBy(F.desc("years_in_top3"))
    write_output(frequency, SECTION, "q3_top3_frequency")
    comparison.show(60, truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
