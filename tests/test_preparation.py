"""Tests for the preparation step on the hand written sample."""

from imdb.preparation.clean import clean_all
from imdb.preparation.null_profile import profile_all
from imdb.preparation.quality_checks import build_checks
from imdb.preparation.schema import typed_tables


def test_null_profile_counts_marker_and_blank(spark, raw_dir):
    rows = {
        (r["table"], r["column"]): r
        for r in profile_all(spark, raw_dir).collect()
    }
    # nm4 rows: empty primaryName once, \N professions twice.
    assert rows[("name.basics", "primaryName")]["missing_rows"] == 1
    assert rows[("name.basics", "primaryProfession")]["missing_rows"] == 2
    assert rows[("name.basics", "deathYear")]["missing_pct"] == 60.0
    assert rows[("title.basics", "tconst")]["missing_rows"] == 0


def test_quality_checks_find_known_problems(spark, raw_dir):
    checks = {
        name: df.count()
        for name, _, _, df in build_checks(typed_tables(spark, raw_dir))
    }
    assert checks["death_before_birth"] == 1
    assert checks["duplicate_nconst"] == 2
    assert checks["end_before_start"] == 1
    assert checks["non_positive_runtime"] == 1
    assert checks["invalid_is_adult"] == 1
    assert checks["rating_out_of_range"] == 1
    assert checks["orphan_principal_name"] == 1
    assert checks["orphan_rating_title"] == 1
    assert checks["orphan_aka_title"] == 1
    assert checks["orphan_crew_writer"] == 1
    assert checks["orphan_episode_title"] == 1
    assert checks["orphan_known_for_title"] == 1
    assert checks["credit_before_birth"] == 1
    assert checks["episode_missing_numbers"] == 1


def test_clean_applies_rules(spark, raw_dir):
    clean = clean_all(typed_tables(spark, raw_dir))

    names = {r["nconst"]: r for r in clean["name_basics"].collect()}
    assert len(names) == 4
    assert names["nm3"]["birthYear"] is None
    assert names["nm3"]["deathYear"] is None
    assert names["nm3"]["dq_invalid_lifespan"] is True
    assert names["nm3"]["knownForTitles"] is None
    assert names["nm1"]["knownForTitles"] == ["tt1", "tt2"]

    basics = {r["tconst"]: r for r in clean["title_basics"].collect()}
    assert basics["tt2"]["runtimeMinutes"] is None
    assert basics["tt3"]["endYear"] is None
    assert basics["tt4"]["isAdult"] is None

    crew = {r["tconst"]: r for r in clean["title_crew"].collect()}
    assert crew["tt1"]["writers"] == ["nm2"]

    assert clean["title_principals"].count() == 3
    assert [r["tconst"] for r in clean["title_ratings"].collect()] == ["tt1"]
    assert clean["title_akas"].count() == 2
    assert clean["title_episode"].count() == 1


def test_clean_flags_missing_death_year(spark):
    from imdb.preparation.clean import clean_names
    names = spark.createDataFrame(
        [("nm_old", "Old", 1850, None), ("nm_young", "Young", 1990, None)],
        "nconst STRING, primaryName STRING, birthYear INT, deathYear INT")
    rows = {r["nconst"]: r for r in clean_names(names).collect()}
    assert rows["nm_old"]["birthYear"] == 1850
    assert rows["nm_old"]["dq_missing_death_year"] is True
    assert rows["nm_young"]["dq_missing_death_year"] is False
