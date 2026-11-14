"""Q6: actors and actresses who were successful in films of several original
languages (at least 2, and at least 3).

A film is successful when its rating is at least SUCCESS_RATING and it has at
least SUCCESS_VOTES votes. Original language comes from languages.py.

Usage: python -m imdb.exploration.q6_multilingual_actors
"""

import os

from pyspark.sql import functions as F

from imdb.common import get_spark, write_output
from imdb.exploration.base import (actor_credits, feature_movies, rated,
                                   with_names)
from imdb.exploration.languages import original_languages

SECTION = "exploration"
SUCCESS_RATING = float(os.environ.get("Q6_SUCCESS_RATING", "7.0"))
SUCCESS_VOTES = int(os.environ.get("Q6_SUCCESS_VOTES", "5000"))


def successful_films(spark):
    films = rated(spark, feature_movies(spark), SUCCESS_VOTES)
    return films.where(F.col("averageRating") >= SUCCESS_RATING) \
        .join(original_languages(spark), "tconst") \
        .select("tconst", "primaryTitle", "original_language")


def multilingual_actors(spark, min_languages=2):
    credits = actor_credits(spark).join(successful_films(spark), "tconst")
    per_actor = credits.groupBy("nconst").agg(
        F.countDistinct("original_language").alias("languages"),
        F.array_sort(F.collect_set("original_language"))
        .alias("language_list"),
        F.count("*").alias("successful_films"),
    ).where(F.col("languages") >= min_languages)
    return with_names(spark, per_actor).select(
        "nconst", "primaryName", "languages", "language_list",
        "successful_films")


def main():
    spark = get_spark("imdb-q6")
    two = multilingual_actors(spark, 2).cache()
    three = two.where(F.col("languages") >= 3)
    order = [F.desc("languages"), F.desc("successful_films"), "primaryName"]
    n_two = write_output(two.orderBy(*order), SECTION,
                         "q6_actors_2plus_languages")
    n_three = write_output(three.orderBy(*order), SECTION,
                           "q6_actors_3plus_languages")
    pairs = (
        two.where(F.col("languages") == 2)
        .groupBy(F.concat_ws(" + ", "language_list").alias("languages"))
        .count().orderBy(F.desc("count")).limit(20)
    )
    write_output(pairs, SECTION, "q6_language_pairs")
    print(f"{n_two} actors with 2+ languages, {n_three} with 3+")
    three.orderBy(*order).show(30, truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
