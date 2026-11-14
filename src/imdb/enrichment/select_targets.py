"""Select the films and principals to enrich (cleaned data, Spark).

Films: feature-length movies (same rule as the exploration step) released
between FIRST_YEAR and LAST_YEAR, ranked inside each (year, genre) by number
of IMDb votes (then rating), keeping the top ENRICH_TOP_N.
Principals: the first ENRICH_PRINCIPALS credits of each selected film in
IMDb billing order (``ordering``).

``ENRICH_TOP_N=0`` and ``ENRICH_PRINCIPALS=0`` remove the limits, so the same
code runs on the whole IMDb dataset without any change.

Usage: python -m imdb.enrichment.select_targets
"""

from pyspark.sql import Window
from pyspark.sql import functions as F

from imdb.common import get_spark, read_clean, write_output
from imdb.enrichment import config as C
from imdb.exploration.base import by_genre, feature_movies, rated


def top_films_per_genre_year(rated_films, first_year, last_year, top_n):
    """One row per (film, genre) with its rank inside (year, genre)."""
    in_range = rated_films.where(
        F.col("startYear").between(first_year, last_year))
    rank = Window.partitionBy("startYear", "genre").orderBy(
        F.desc("numVotes"), F.desc("averageRating"), "tconst")
    ranked = by_genre(in_range).withColumn("rank", F.row_number().over(rank))
    if top_n > 0:
        ranked = ranked.where(F.col("rank") <= top_n)
    return ranked.select(
        "tconst", "primaryTitle", "originalTitle",
        F.col("startYear").alias("year"), "genre", "rank",
        "runtimeMinutes", "averageRating", "numVotes",
    )


def top_principals(principals, names, film_ids, n_principals):
    """First ``n_principals`` distinct people of each film (billing order)."""
    first_credit = Window.partitionBy("tconst", "nconst").orderBy("ordering")
    billing = Window.partitionBy("tconst").orderBy("ordering", "nconst")
    selected = (
        principals.join(film_ids, "tconst", "left_semi")
        .withColumn("_n", F.row_number().over(first_credit))
        .where(F.col("_n") == 1)
        .withColumn("principal_rank", F.row_number().over(billing))
    )
    if n_principals > 0:
        selected = selected.where(F.col("principal_rank") <= n_principals)
    people = names.select("nconst", "primaryName", "birthYear", "deathYear")
    return selected.join(people, "nconst", "left").select(
        "tconst", "nconst", "principal_rank", "ordering", "category",
        "characters", "primaryName", "birthYear", "deathYear",
    )


def main():
    spark = get_spark("enrichment-select-targets")
    films = top_films_per_genre_year(
        rated(spark, feature_movies(spark)), C.FIRST_YEAR, C.LAST_YEAR,
        C.TOP_N)
    films.write.mode("overwrite").parquet(C.TARGET_FILMS)
    films = spark.read.parquet(C.TARGET_FILMS)

    film_ids = films.select("tconst").distinct()
    people = top_principals(read_clean(spark, "title_principals"),
                            read_clean(spark, "name_basics"), film_ids,
                            C.N_PRINCIPALS)
    people.write.mode("overwrite").parquet(C.TARGET_PRINCIPALS)
    people = spark.read.parquet(C.TARGET_PRINCIPALS)

    # ID lists read by the (non-Spark) gathering script.
    for ids, path in (
            (film_ids.select(F.col("tconst").alias("imdb_id")),
             C.TARGET_FILM_IDS),
            (people.select(F.col("nconst").alias("imdb_id")).distinct(),
             C.TARGET_PERSON_IDS)):
        ids.coalesce(1).write.mode("overwrite").option("header", "true") \
            .csv(path)

    summary = spark.createDataFrame([
        ("(film, genre, year) rows", films.count()),
        ("distinct films", film_ids.count()),
        ("(film, principal) rows", people.count()),
        ("distinct people", people.select("nconst").distinct().count()),
    ], "measure STRING, value LONG")
    write_output(summary, C.SECTION, "targets_summary")
    summary.show(truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
