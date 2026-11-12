"""Data quality checks on the typed IMDb tables.

Each check returns the offending rows. The summary lists, for every check,
the number of rows affected and the share of the table they represent, and a
sample of the offending rows is saved next to it.

Usage: python -m imdb.preparation.quality_checks
"""

import os

from pyspark.sql import functions as F

from imdb.common import get_spark, write_output
from imdb.preparation.schema import typed_tables

SECTION = "preparation"
REFERENCE_YEAR = int(os.environ.get("IMDB_REFERENCE_YEAR", "2026"))
MAX_LIFESPAN = 120


def _orphans(child, key, parent, parent_key):
    """Rows of child whose non-null key has no match in parent."""
    parent_keys = parent.select(F.col(parent_key).alias(key)).distinct()
    return child.where(F.col(key).isNotNull()).join(
        parent_keys, on=key, how="left_anti")


def _exploded_orphans(child, array_col, parent, parent_key, alias):
    """Exploded array elements of child with no match in parent."""
    exploded = child.select(
        "tconst" if "tconst" in child.columns else child.columns[0],
        F.explode(array_col).alias(alias),
    )
    return _orphans(exploded, alias, parent, parent_key)


def _duplicates(df, key):
    """Rows whose primary key appears more than once."""
    dup_keys = df.groupBy(key).count().where(F.col("count") > 1).select(key)
    return df.join(dup_keys, on=key, how="left_semi")


def build_checks(t):
    """Return a list of (name, table, description, offending_df)."""
    names = t["name.basics"]
    basics = t["title.basics"]
    akas = t["title.akas"]
    crew = t["title.crew"]
    episode = t["title.episode"]
    principals = t["title.principals"]
    ratings = t["title.ratings"]

    person_years = names.select("nconst", "birthYear", "deathYear")
    credits = (
        principals.select("tconst", "nconst", "category")
        .join(basics.select("tconst", "startYear"), "tconst")
        .join(person_years, "nconst")
    )

    return [
        # Primary key problems.
        ("duplicate_nconst", "name.basics",
         "Same nconst appears more than once", _duplicates(names, "nconst")),
        ("duplicate_tconst", "title.basics",
         "Same tconst appears more than once", _duplicates(basics, "tconst")),
        ("null_primary_key_title", "title.basics",
         "tconst is missing", basics.where(F.col("tconst").isNull())),

        # Impossible or suspicious dates for people.
        ("death_before_birth", "name.basics",
         "deathYear is earlier than birthYear",
         names.where(F.col("deathYear") < F.col("birthYear"))),
        ("lifespan_over_120", "name.basics",
         f"deathYear - birthYear is greater than {MAX_LIFESPAN}",
         names.where(F.col("deathYear") - F.col("birthYear")
                     > MAX_LIFESPAN)),
        ("alive_over_120", "name.basics",
         f"No deathYear but born more than {MAX_LIFESPAN} years ago",
         names.where(F.col("deathYear").isNull()
                     & (F.col("birthYear") < REFERENCE_YEAR - MAX_LIFESPAN))),
        ("birth_or_death_in_future", "name.basics",
         f"birthYear or deathYear after {REFERENCE_YEAR}",
         names.where((F.col("birthYear") > REFERENCE_YEAR)
                     | (F.col("deathYear") > REFERENCE_YEAR))),
        ("credit_before_birth", "title.principals",
         "Principal credited on a title released before their birth",
         credits.where(F.col("startYear") < F.col("birthYear"))),
        ("credit_long_after_death", "title.principals",
         "Principal (not archive footage) credited more than 10 years "
         "after death",
         credits.where((F.col("startYear") > F.col("deathYear") + 10)
                       & (F.col("category") != "archive_footage")
                       & (F.col("category") != "archive_sound"))),

        # Impossible values for titles.
        ("end_before_start", "title.basics",
         "endYear is earlier than startYear",
         basics.where(F.col("endYear") < F.col("startYear"))),
        ("start_year_in_future", "title.basics",
         f"startYear after {REFERENCE_YEAR} (announced titles)",
         basics.where(F.col("startYear") > REFERENCE_YEAR)),
        ("non_positive_runtime", "title.basics",
         "runtimeMinutes is zero or negative",
         basics.where(F.col("runtimeMinutes") <= 0)),
        ("invalid_is_adult", "title.basics",
         "isAdult is not 0 or 1",
         basics.where(F.col("isAdult").isNotNull()
                      & ~F.col("isAdult").isin(0, 1))),
        ("more_than_three_genres", "title.basics",
         "More than three genres (IMDb allows at most three)",
         basics.where(F.size("genres") > 3)),
        ("rating_out_of_range", "title.ratings",
         "averageRating outside [1, 10] or numVotes below 1",
         ratings.where(~F.col("averageRating").between(1.0, 10.0)
                       | (F.col("numVotes") < 1))),
        ("episode_missing_numbers", "title.episode",
         "seasonNumber or episodeNumber is missing",
         episode.where(F.col("seasonNumber").isNull()
                       | F.col("episodeNumber").isNull())),
        ("episode_parent_not_series", "title.episode",
         "Parent title exists but is not a tvSeries or tvMiniSeries",
         episode.join(
             basics.select(F.col("tconst").alias("parentTconst"),
                           "titleType"),
             "parentTconst")
         .where(~F.col("titleType").isin("tvSeries", "tvMiniSeries"))),

        # Foreign keys without a parent record.
        ("orphan_principal_title", "title.principals",
         "tconst not found in title.basics",
         _orphans(principals, "tconst", basics, "tconst")),
        ("orphan_principal_name", "title.principals",
         "nconst not found in name.basics",
         _orphans(principals, "nconst", names, "nconst")),
        ("orphan_rating_title", "title.ratings",
         "tconst not found in title.basics",
         _orphans(ratings, "tconst", basics, "tconst")),
        ("orphan_aka_title", "title.akas",
         "titleId not found in title.basics",
         _orphans(akas, "titleId", basics, "tconst")),
        ("orphan_crew_title", "title.crew",
         "tconst not found in title.basics",
         _orphans(crew, "tconst", basics, "tconst")),
        ("orphan_crew_director", "title.crew",
         "Director nconst not found in name.basics",
         _exploded_orphans(crew, "directors", names, "nconst", "nconst")),
        ("orphan_crew_writer", "title.crew",
         "Writer nconst not found in name.basics",
         _exploded_orphans(crew, "writers", names, "nconst", "nconst")),
        ("orphan_episode_title", "title.episode",
         "Episode tconst not found in title.basics",
         _orphans(episode, "tconst", basics, "tconst")),
        ("orphan_episode_parent", "title.episode",
         "parentTconst not found in title.basics",
         _orphans(episode, "parentTconst", basics, "tconst")),
        ("orphan_known_for_title", "name.basics",
         "knownForTitles entry not found in title.basics",
         _orphans(names.select("nconst",
                               F.explode("knownForTitles").alias("tconst")),
                  "tconst", basics, "tconst")),
    ]


def run_checks(spark, raw_dir=None, output_dir=None, sample_rows=20):
    """Run every check and return the summary DataFrame."""
    tables = typed_tables(spark, raw_dir)
    table_sizes = {name: df.count() for name, df in tables.items()}
    summary = []
    for name, table, description, offending in build_checks(tables):
        count = offending.count()
        total = table_sizes[table]
        pct = round(100.0 * count / total, 4) if total else 0.0
        summary.append((name, table, description, count, pct))
        if count:
            write_output(offending.limit(sample_rows), SECTION,
                         f"dq_sample_{name}", output_dir)
    return spark.createDataFrame(
        summary,
        "check STRING, table STRING, description STRING, "
        "affected_rows LONG, affected_pct DOUBLE",
    )


def main():
    spark = get_spark("imdb-quality-checks")
    summary = run_checks(spark)
    write_output(summary, SECTION, "dq_summary", preview_rows=100)
    summary.show(100, truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
