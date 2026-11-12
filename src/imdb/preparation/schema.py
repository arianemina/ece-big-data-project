"""Schema enforcement: convert raw IMDb string columns to typed columns.

"\\N" and blank strings become real nulls, numbers are cast and the comma
separated list columns become arrays. No row is removed at this stage.
"""

from pyspark.sql import functions as F

from imdb.common import as_double, as_int, as_str, read_raw, split_list

CHARACTERS_SCHEMA = "array<string>"


def typed_name_basics(spark, raw_dir=None):
    raw = read_raw(spark, "name.basics", raw_dir)
    return raw.select(
        as_str("nconst").alias("nconst"),
        as_str("primaryName").alias("primaryName"),
        as_int("birthYear").alias("birthYear"),
        as_int("deathYear").alias("deathYear"),
        split_list("primaryProfession").alias("primaryProfession"),
        split_list("knownForTitles").alias("knownForTitles"),
    )


def typed_title_basics(spark, raw_dir=None):
    raw = read_raw(spark, "title.basics", raw_dir)
    return raw.select(
        as_str("tconst").alias("tconst"),
        as_str("titleType").alias("titleType"),
        as_str("primaryTitle").alias("primaryTitle"),
        as_str("originalTitle").alias("originalTitle"),
        as_int("isAdult").alias("isAdult"),
        as_int("startYear").alias("startYear"),
        as_int("endYear").alias("endYear"),
        as_int("runtimeMinutes").alias("runtimeMinutes"),
        split_list("genres").alias("genres"),
    )


def typed_title_akas(spark, raw_dir=None):
    raw = read_raw(spark, "title.akas", raw_dir)
    return raw.select(
        as_str("titleId").alias("titleId"),
        as_int("ordering").alias("ordering"),
        as_str("title").alias("title"),
        as_str("region").alias("region"),
        as_str("language").alias("language"),
        # types and attributes use the 0x02 control character as separator.
        F.when(as_str("types").isNull(), F.lit(None))
        .otherwise(F.split(F.col("types"), "\u0002")).alias("types"),
        F.when(as_str("attributes").isNull(), F.lit(None))
        .otherwise(F.split(F.col("attributes"), "\u0002"))
        .alias("attributes"),
        as_int("isOriginalTitle").alias("isOriginalTitle"),
    )


def typed_title_crew(spark, raw_dir=None):
    raw = read_raw(spark, "title.crew", raw_dir)
    return raw.select(
        as_str("tconst").alias("tconst"),
        split_list("directors").alias("directors"),
        split_list("writers").alias("writers"),
    )


def typed_title_episode(spark, raw_dir=None):
    raw = read_raw(spark, "title.episode", raw_dir)
    return raw.select(
        as_str("tconst").alias("tconst"),
        as_str("parentTconst").alias("parentTconst"),
        as_int("seasonNumber").alias("seasonNumber"),
        as_int("episodeNumber").alias("episodeNumber"),
    )


def typed_title_principals(spark, raw_dir=None):
    raw = read_raw(spark, "title.principals", raw_dir)
    return raw.select(
        as_str("tconst").alias("tconst"),
        as_int("ordering").alias("ordering"),
        as_str("nconst").alias("nconst"),
        as_str("category").alias("category"),
        as_str("job").alias("job"),
        F.from_json(as_str("characters"), CHARACTERS_SCHEMA)
        .alias("characters"),
    )


def typed_title_ratings(spark, raw_dir=None):
    raw = read_raw(spark, "title.ratings", raw_dir)
    return raw.select(
        as_str("tconst").alias("tconst"),
        as_double("averageRating").alias("averageRating"),
        as_int("numVotes").alias("numVotes"),
    )


TYPED_READERS = {
    "name.basics": typed_name_basics,
    "title.akas": typed_title_akas,
    "title.basics": typed_title_basics,
    "title.crew": typed_title_crew,
    "title.episode": typed_title_episode,
    "title.principals": typed_title_principals,
    "title.ratings": typed_title_ratings,
}


def typed_tables(spark, raw_dir=None):
    """Return a dict of every typed IMDb table."""
    return {name: reader(spark, raw_dir)
            for name, reader in TYPED_READERS.items()}
