"""Q8: multi-talented film professionals (actor / director / writer) and how
their movies perform when they hold several roles on the same movie.

Roles come from title.principals (actor, actress, director, writer) and from
title.crew (directors, writers), on rated feature-length movies. A person is
multi-talented when they hold at least two of the three roles, each on at
least MIN_CREDITS_PER_ROLE different movies.

Usage: python -m imdb.exploration.q8_multi_talented
"""

import os

from pyspark.sql import functions as F

from imdb.common import get_spark, read_clean, write_output
from imdb.exploration.base import feature_movies, rated, with_names

SECTION = "exploration"
MIN_CREDITS_PER_ROLE = int(os.environ.get("Q8_MIN_CREDITS", "3"))
MIN_VOTES = int(os.environ.get("Q8_MIN_VOTES", "100"))
ROLE_OF_CATEGORY = {"actor": "actor", "actress": "actor",
                    "director": "director", "writer": "writer"}


def roles_per_movie(spark, min_votes=MIN_VOTES):
    """One row per (person, movie) with the set of roles held."""
    movies = rated(spark, feature_movies(spark), min_votes).select(
        "tconst", "averageRating", "numVotes")
    principals = read_clean(spark, "title_principals")
    mapping = F.create_map(*[F.lit(x) for kv in ROLE_OF_CATEGORY.items()
                             for x in kv])
    from_principals = principals.select(
        "tconst", "nconst", mapping[F.col("category")].alias("role")
    ).where(F.col("role").isNotNull())
    crew = read_clean(spark, "title_crew")
    from_directors = crew.select(
        "tconst", F.explode("directors").alias("nconst"),
        F.lit("director").alias("role"))
    from_writers = crew.select(
        "tconst", F.explode("writers").alias("nconst"),
        F.lit("writer").alias("role"))
    roles = from_principals.unionByName(from_directors) \
        .unionByName(from_writers).distinct()
    return roles.join(movies, "tconst").groupBy(
        "nconst", "tconst", "averageRating", "numVotes").agg(
        F.array_sort(F.collect_set("role")).alias("roles"))


def multi_talented(person_movies, min_credits=MIN_CREDITS_PER_ROLE):
    exploded = person_movies.select("nconst", F.explode("roles").alias("r"))
    per_role = exploded.groupBy("nconst", "r").count() \
        .where(F.col("count") >= min_credits)
    return per_role.groupBy("nconst").agg(
        F.array_sort(F.collect_list("r")).alias("talents")) \
        .where(F.size("talents") >= 2)


def performance(person_movies, talented):
    """Compare movies where the person had one role vs several roles."""
    movies = person_movies.join(talented, "nconst").withColumn(
        "mode", F.when(F.size("roles") > 1, "multiple_roles")
        .otherwise("single_role"))
    per_person = movies.groupBy("nconst", "talents").pivot(
        "mode", ["single_role", "multiple_roles"]).agg(
        F.count("tconst").alias("movies"),
        F.round(F.avg("averageRating"), 2).alias("avg_rating"),
        F.round(F.avg("numVotes"), 0).alias("avg_votes"))
    per_person = per_person.withColumn(
        "rating_gain",
        F.round(F.col("multiple_roles_avg_rating")
                - F.col("single_role_avg_rating"), 2))
    combos = movies.where(F.col("mode") == "multiple_roles").groupBy(
        F.concat_ws("+", "roles").alias("role_combination")).agg(
        F.countDistinct("nconst").alias("people"),
        F.count("*").alias("person_movies"),
        F.round(F.avg("averageRating"), 3).alias("avg_rating"),
        F.round(F.avg("numVotes"), 0).alias("avg_votes"))
    single = movies.where(F.col("mode") == "single_role").agg(
        F.lit("single role (baseline)").alias("role_combination"),
        F.countDistinct("nconst").alias("people"),
        F.count("*").alias("person_movies"),
        F.round(F.avg("averageRating"), 3).alias("avg_rating"),
        F.round(F.avg("numVotes"), 0).alias("avg_votes"))
    return per_person, combos.unionByName(single)


def main():
    spark = get_spark("imdb-q8")
    person_movies = roles_per_movie(spark).cache()
    talented = multi_talented(person_movies).cache()
    per_person, combos = performance(person_movies, talented)
    per_person = with_names(spark, per_person).where(
        F.col("multiple_roles_movies").isNotNull())
    n_people = write_output(
        with_names(spark, talented).select(
            "nconst", "primaryName", F.concat_ws(", ", "talents")
            .alias("talents")).orderBy("primaryName"),
        SECTION, "q8_multi_talented_people")
    write_output(per_person.select(
        "nconst", "primaryName", F.concat_ws(", ", "talents")
        .alias("talents"), "single_role_movies", "single_role_avg_rating",
        "multiple_roles_movies", "multiple_roles_avg_rating", "rating_gain")
        .orderBy(F.desc("multiple_roles_movies")),
        SECTION, "q8_performance_per_person")
    write_output(combos.orderBy(F.desc("person_movies")), SECTION,
                 "q8_performance_by_combination")
    summary = per_person.agg(
        F.count("*").alias("people_with_both_modes"),
        F.sum(F.when(F.col("rating_gain") > 0, 1).otherwise(0))
        .alias("better_with_multiple_roles"),
        F.sum(F.when(F.col("rating_gain") < 0, 1).otherwise(0))
        .alias("worse_with_multiple_roles"),
        F.round(F.avg("rating_gain"), 3).alias("avg_rating_gain"))
    write_output(summary, SECTION, "q8_summary")
    print(f"{n_people} multi-talented people")
    combos.show(truncate=False)
    summary.show(truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
