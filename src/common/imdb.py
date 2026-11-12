"""IMDb dataset schemas and readers.

Raw files are the TSV.gz files from https://datasets.imdbws.com/ stored in
``data/raw``. ``src.ingest_imdb`` converts them once into Parquet files in
``data/parquet`` with explicit schemas; every other job reads the Parquet
version through :func:`read_table`.
"""
import os

from pyspark.sql import types as T

DATA_DIR = os.environ.get("DATA_DIR", "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PARQUET_DIR = os.path.join(DATA_DIR, "parquet")

S, I, F, B = T.StringType(), T.IntegerType(), T.DoubleType(), T.BooleanType()

# Array-like columns (comma separated in the TSV) are kept as strings here so
# that the raw content stays untouched; split them where needed.
SCHEMAS = {
    "name.basics": [
        ("nconst", S), ("primaryName", S), ("birthYear", I),
        ("deathYear", I), ("primaryProfession", S), ("knownForTitles", S),
    ],
    "title.akas": [
        ("titleId", S), ("ordering", I), ("title", S), ("region", S),
        ("language", S), ("types", S), ("attributes", S),
        ("isOriginalTitle", B),
    ],
    "title.basics": [
        ("tconst", S), ("titleType", S), ("primaryTitle", S),
        ("originalTitle", S), ("isAdult", B), ("startYear", I),
        ("endYear", I), ("runtimeMinutes", I), ("genres", S),
    ],
    "title.crew": [
        ("tconst", S), ("directors", S), ("writers", S),
    ],
    "title.episode": [
        ("tconst", S), ("parentTconst", S), ("seasonNumber", I),
        ("episodeNumber", I),
    ],
    "title.principals": [
        ("tconst", S), ("ordering", I), ("nconst", S), ("category", S),
        ("job", S), ("characters", S),
    ],
    "title.ratings": [
        ("tconst", S), ("averageRating", F), ("numVotes", I),
    ],
}

TABLES = list(SCHEMAS)


def schema(table):
    """Return the Spark StructType of an IMDb table."""
    return T.StructType(
        [T.StructField(name, dtype, True) for name, dtype in SCHEMAS[table]]
    )


def read_raw(spark, table, raw_dir=RAW_DIR):
    """Read a raw IMDb TSV.gz file with its explicit schema.

    IMDb encodes missing values as ``\\N``. Quotes are not used as text
    qualifiers in these files, so quoting is disabled.
    """
    return (
        spark.read.option("sep", "\t")
        .option("header", "true")
        .option("nullValue", "\\N")
        .option("quote", "")
        .option("mode", "PERMISSIVE")
        .schema(schema(table))
        .csv(os.path.join(raw_dir, f"{table}.tsv.gz"))
    )


def read_table(spark, table, parquet_dir=PARQUET_DIR):
    """Read the Parquet version of an IMDb table."""
    return spark.read.parquet(os.path.join(parquet_dir, table))
