"""Shared helpers: Spark session, paths, IMDb readers and output writers."""

import os

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

RAW_DIR = os.environ.get("IMDB_RAW_DIR", "data/raw")
CLEAN_DIR = os.environ.get("IMDB_CLEAN_DIR", "data/clean")
OUTPUT_DIR = os.environ.get("IMDB_OUTPUT_DIR", "output")

# IMDb encodes missing values with the literal string "\N".
IMDB_NULL = "\\N"

# Column layout of every IMDb table (all columns are read as strings first).
RAW_TABLES = {
    "name.basics": [
        "nconst", "primaryName", "birthYear", "deathYear",
        "primaryProfession", "knownForTitles",
    ],
    "title.akas": [
        "titleId", "ordering", "title", "region", "language", "types",
        "attributes", "isOriginalTitle",
    ],
    "title.basics": [
        "tconst", "titleType", "primaryTitle", "originalTitle", "isAdult",
        "startYear", "endYear", "runtimeMinutes", "genres",
    ],
    "title.crew": ["tconst", "directors", "writers"],
    "title.episode": [
        "tconst", "parentTconst", "seasonNumber", "episodeNumber",
    ],
    "title.principals": [
        "tconst", "ordering", "nconst", "category", "job", "characters",
    ],
    "title.ratings": ["tconst", "averageRating", "numVotes"],
}


def get_spark(app_name="imdb"):
    """Create (or reuse) a local Spark session sized by environment vars."""
    return (
        SparkSession.builder
        .appName(app_name)
        .master(os.environ.get("SPARK_MASTER", "local[*]"))
        .config("spark.driver.memory",
                os.environ.get("SPARK_DRIVER_MEMORY", "4g"))
        .config("spark.sql.shuffle.partitions",
                os.environ.get("SPARK_SHUFFLE_PARTITIONS", "64"))
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


def raw_path(table, raw_dir=None):
    """Return the path of a raw IMDb file (gzip or plain TSV)."""
    base = raw_dir or RAW_DIR
    gz = os.path.join(base, f"{table}.tsv.gz")
    return gz if os.path.exists(gz) else os.path.join(base, f"{table}.tsv")


def read_raw(spark, table, raw_dir=None):
    """Read a raw IMDb TSV with every column as an untouched string.

    Quoting is disabled because IMDb titles contain unbalanced double quotes,
    and "\\N" is kept as a literal so that missing values can be profiled.
    """
    columns = RAW_TABLES[table]
    schema = ", ".join(f"`{c}` STRING" for c in columns)
    return (
        spark.read
        .option("sep", "\t")
        .option("header", "true")
        .option("quote", "")
        .option("mode", "PERMISSIVE")
        .schema(schema)
        .csv(raw_path(table, raw_dir))
    )


def read_clean(spark, table, clean_dir=None):
    """Read a cleaned table written by the preparation step."""
    base = clean_dir or CLEAN_DIR
    return spark.read.parquet(os.path.join(base, table))


def is_missing(column):
    """Spark condition that is true when a raw value is null, \\N or blank."""
    col = F.col(column)
    return col.isNull() | (col == IMDB_NULL) | (F.trim(col) == "")


def write_output(df, section, name, output_dir=None, preview_rows=50):
    """Save a result as CSV plus a Markdown preview for REPORT.md."""
    base = os.path.join(output_dir or OUTPUT_DIR, section)
    os.makedirs(base, exist_ok=True)
    df = flatten_for_csv(df)
    (
        df.coalesce(1)
        .write.mode("overwrite")
        .option("header", "true")
        .csv(os.path.join(base, name))
    )
    rows = df.limit(preview_rows).collect()
    total = df.count()
    with open(os.path.join(base, f"{name}.md"), "w", encoding="utf-8") as fh:
        fh.write(to_markdown(df.columns, rows))
        fh.write(f"\n_{total} rows in total")
        if total > preview_rows:
            fh.write(f", first {preview_rows} shown")
        fh.write("._\n")
    return total


def flatten_for_csv(df):
    """Turn array, map and struct columns into strings (CSV friendly)."""
    columns = []
    for field in df.schema.fields:
        name = field.name
        kind = field.dataType.typeName()
        if kind == "array" and field.dataType.elementType.typeName() in (
                "string", "integer", "long", "double"):
            columns.append(F.concat_ws(",", F.col(name)).alias(name))
        elif kind in ("array", "map", "struct"):
            columns.append(F.to_json(F.col(name)).alias(name))
        else:
            columns.append(F.col(name))
    return df.select(*columns)


def to_markdown(columns, rows):
    """Render rows as a Markdown table."""
    def fmt(value):
        if value is None:
            return ""
        if isinstance(value, float):
            return f"{value:.2f}"
        if isinstance(value, (list, tuple)):
            return ", ".join(str(v) for v in value)
        return str(value).replace("|", "\\|")

    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(fmt(v) for v in row) + " |")
    return "\n".join(lines) + "\n"


def split_list(column):
    """Split an IMDb comma separated column into an array (null if missing)."""
    return F.when(is_missing(column), F.lit(None)).otherwise(
        F.split(F.col(column), ",")
    )


def as_int(column):
    """Cast a raw string to int, treating \\N, blanks and garbage as null."""
    return F.when(is_missing(column), F.lit(None)).otherwise(
        F.col(column).try_cast("int")
    )


def as_double(column):
    """Cast a raw string to double, treating \\N and blanks as null."""
    return F.when(is_missing(column), F.lit(None)).otherwise(
        F.col(column).try_cast("double")
    )


def as_str(column):
    """Return the string value, or null when it is \\N or blank."""
    return F.when(is_missing(column), F.lit(None)).otherwise(F.col(column))


def unpersist_all(*frames: DataFrame):
    """Release cached DataFrames."""
    for frame in frames:
        frame.unpersist()
