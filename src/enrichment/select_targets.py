"""Select the films and principals to enrich (Spark).

By default: feature-length films (>= 40 min) released 1980-2025, the top 10
films per (year, genre) ranked by number of IMDb votes, and the first three
principals (IMDb billing order) of each selected film.

Every limit is a parameter; ``--top-n 0`` / ``--principals 0`` remove the
limits so the same code runs on the full IMDb dataset.

Usage:
    python -m src.enrichment.select_targets [--top-n 10] [--principals 3]
"""
import argparse

from pyspark.sql import Window
from pyspark.sql import functions as F

from src.common.imdb import read_table
from src.common.spark import get_spark
from src.enrichment import config as C


def feature_films(basics, year_from, year_to, min_runtime,
                  include_adult=False):
    """Feature-length movies released in [year_from, year_to]."""
    films = basics.filter(
        (F.col("titleType") == "movie")
        & (F.col("runtimeMinutes") >= min_runtime)
        & F.col("startYear").between(year_from, year_to)
    )
    if not include_adult:
        films = films.filter(~F.coalesce(F.col("isAdult"), F.lit(False)))
    return films


def top_films_per_genre_year(films, ratings, top_n):
    """Rank films inside each (year, genre) by votes, then rating.

    Returns one row per (film, genre). ``top_n`` <= 0 keeps every film.
    """
    exploded = (
        films.join(ratings, "tconst", "inner")
        .withColumn("genre", F.explode(F.split("genres", ",")))
    )
    w = Window.partitionBy("startYear", "genre").orderBy(
        F.desc("numVotes"), F.desc("averageRating"), F.asc("tconst")
    )
    ranked = exploded.withColumn("rank", F.row_number().over(w))
    if top_n > 0:
        ranked = ranked.filter(F.col("rank") <= top_n)
    return ranked.select(
        "tconst", "primaryTitle", "originalTitle",
        F.col("startYear").alias("year"), "genre", "rank",
        "runtimeMinutes", "averageRating", "numVotes",
    )


def top_principals(principals, names, film_ids, n_principals):
    """First ``n_principals`` principals of each film (billing order)."""
    w = Window.partitionBy("tconst").orderBy("ordering", "nconst")
    selected = (
        principals.join(film_ids, "tconst", "left_semi")
        .dropDuplicates(["tconst", "nconst"])
        .withColumn("principal_rank", F.row_number().over(w))
    )
    if n_principals > 0:
        selected = selected.filter(F.col("principal_rank") <= n_principals)
    return (
        selected.join(names.select("nconst", "primaryName", "birthYear",
                                   "deathYear"), "nconst", "left")
        .select("tconst", "nconst", "principal_rank", "ordering",
                "category", "characters", "primaryName", "birthYear",
                "deathYear")
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year-from", type=int, default=C.YEAR_FROM)
    parser.add_argument("--year-to", type=int, default=C.YEAR_TO)
    parser.add_argument("--min-runtime", type=int, default=C.MIN_RUNTIME)
    parser.add_argument("--top-n", type=int, default=C.TOP_N)
    parser.add_argument("--principals", type=int, default=C.N_PRINCIPALS)
    args = parser.parse_args()

    spark = get_spark("enrichment-select-targets")
    basics = read_table(spark, "title.basics")
    ratings = read_table(spark, "title.ratings")
    principals = read_table(spark, "title.principals")
    names = read_table(spark, "name.basics")

    films = feature_films(basics, args.year_from, args.year_to,
                          args.min_runtime)
    top = top_films_per_genre_year(films, ratings, args.top_n)
    top.write.mode("overwrite").parquet(C.TARGET_FILMS)
    top = spark.read.parquet(C.TARGET_FILMS)

    film_ids = top.select("tconst").distinct()
    people = top_principals(principals, names, film_ids, args.principals)
    people.write.mode("overwrite").parquet(C.TARGET_PRINCIPALS)
    people = spark.read.parquet(C.TARGET_PRINCIPALS)

    film_ids.select(F.col("tconst").alias("imdb_id")) \
        .coalesce(1).write.mode("overwrite").parquet(C.TARGET_FILM_IDS)
    people.select(F.col("nconst").alias("imdb_id")).distinct() \
        .coalesce(1).write.mode("overwrite").parquet(C.TARGET_PERSON_IDS)

    print(f"(film, genre, year) rows : {top.count():,}")
    print(f"distinct films           : {film_ids.count():,}")
    print(f"(film, principal) rows   : {people.count():,}")
    print(f"distinct people          : "
          f"{people.select('nconst').distinct().count():,}")
    spark.stop()


if __name__ == "__main__":
    main()
