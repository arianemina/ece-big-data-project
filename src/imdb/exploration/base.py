"""Common building blocks for the exploration queries (cleaned data only)."""

import os

from pyspark.sql import functions as F

from imdb.common import read_clean

# A feature film runs for more than 40 minutes (Academy / AFI / BFI rule).
FEATURE_MIN_RUNTIME = int(os.environ.get("FEATURE_MIN_RUNTIME", "40"))
ACTING_CATEGORIES = ("actor", "actress")


def feature_movies(spark, include_adult=False):
    """Movies whose runtime makes them feature length."""
    basics = read_clean(spark, "title_basics")
    movies = basics.where(
        (F.col("titleType") == "movie")
        & (F.col("runtimeMinutes") > FEATURE_MIN_RUNTIME)
    )
    if not include_adult:
        movies = movies.where(F.coalesce(F.col("isAdult"), F.lit(0)) == 0)
    return movies


def rated(spark, titles, min_votes=0):
    """Inner join titles with their ratings, keeping enough votes."""
    ratings = read_clean(spark, "title_ratings")
    return titles.join(ratings, "tconst").where(F.col("numVotes") >= min_votes)


def by_genre(titles):
    """One row per (title, genre)."""
    return titles.where(F.col("genres").isNotNull()) \
        .withColumn("genre", F.explode("genres"))


def actor_credits(spark):
    """(tconst, nconst) pairs for actors and actresses."""
    principals = read_clean(spark, "title_principals")
    return principals.where(F.col("category").isin(*ACTING_CATEGORIES)) \
        .select("tconst", "nconst").distinct()


def with_names(spark, df):
    """Add primaryName next to nconst."""
    names = read_clean(spark, "name_basics").select("nconst", "primaryName")
    return df.join(names, "nconst", "left")
