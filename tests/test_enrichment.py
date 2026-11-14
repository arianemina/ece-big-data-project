"""Tests for the enrichment pipeline (no network access needed)."""

import json

from pyspark.sql import functions as F

from imdb.enrichment import build_enriched, fetch_wikipedia, select_targets

FILMS = ("tconst STRING, primaryTitle STRING, originalTitle STRING, "
         "startYear INT, runtimeMinutes INT, genres ARRAY<STRING>, "
         "averageRating DOUBLE, numVotes INT")


def test_top_films_per_genre_year(spark):
    rows = [(f"tt{i}", f"F{i}", f"F{i}", 2000, 100, ["Drama", "Comedy"],
             7.0, 100 * i) for i in range(1, 5)]
    rows.append(("tt9", "Old", "Old", 1970, 100, ["Drama"], 9.0, 10 ** 6))
    films = spark.createDataFrame(rows, FILMS)
    top = select_targets.top_films_per_genre_year(films, 1980, 2025, 2)
    drama = [r.tconst for r in top.where("genre = 'Drama'")
             .orderBy("rank").collect()]
    assert drama == ["tt4", "tt3"]           # most voted first
    assert top.count() == 4                  # 2 genres x top 2
    assert top.where("tconst = 'tt9'").count() == 0   # out of range
    # top_n = 0 keeps everything in range
    assert select_targets.top_films_per_genre_year(
        films, 1980, 2025, 0).count() == 8


def test_top_principals_keeps_first_distinct_people(spark):
    principals = spark.createDataFrame(
        [("tt1", 1, "nm1", "actor", None),
         ("tt1", 2, "nm1", "producer", None),
         ("tt1", 3, "nm2", "actress", None),
         ("tt1", 4, "nm3", "director", None),
         ("tt1", 5, "nm4", "writer", None),
         ("tt2", 1, "nm5", "actor", None)],
        "tconst STRING, ordering INT, nconst STRING, category STRING, "
        "characters ARRAY<STRING>")
    names = spark.createDataFrame(
        [(f"nm{i}", f"P{i}", 1950, None) for i in range(1, 6)],
        "nconst STRING, primaryName STRING, birthYear INT, deathYear INT")
    film_ids = spark.createDataFrame([("tt1",)], "tconst STRING")
    people = select_targets.top_principals(principals, names, film_ids, 3)
    got = [(r.nconst, r.principal_rank) for r in
           people.orderBy("principal_rank").collect()]
    assert got == [("nm1", 1), ("nm2", 2), ("nm3", 3)]


def test_plot_section_and_lead_extraction(spark):
    text = ("Film is a 1999 film directed by Someone.[1]\n\n\n"
            "== Plot ==\nA hero   leaves home.\n\n=== Part two ===\n"
            "He comes back and saves the town from the villain.\n\n\n"
            "== Cast ==\nActor as Hero")
    df = spark.createDataFrame([(text,), ("No sections here at all, only a "
                                          "long enough lead paragraph.",)],
                               "extract STRING")
    out = df.select(
        build_enriched.clean_text(F.regexp_extract(
            "extract", build_enriched.PLOT_REGEX, 1)).alias("plot"),
        build_enriched.clean_text(F.regexp_extract(
            "extract", build_enriched.LEAD_REGEX, 1)).alias("lead"),
    ).collect()
    assert out[0].plot == ("A hero leaves home. He comes back and saves the "
                           "town from the villain.")
    assert out[0].lead == "Film is a 1999 film directed by Someone."
    assert out[1].plot is None
    assert out[1].lead.startswith("No sections here")


def test_latest_record_per_id_wins(spark):
    df = spark.createDataFrame(
        [("tt1", "2026-01-01T00:00:00+00:00", "old"),
         ("tt1", "2026-02-01T00:00:00+00:00", "new")],
        "imdb_id STRING, retrieved_at STRING, value STRING")
    rows = build_enriched.latest_per_id(df).collect()
    assert [r.value for r in rows] == ["new"]


def test_resume_skips_ids_already_fetched(tmp_path):
    path = tmp_path / "out.jsonl"
    fetch_wikipedia.append(str(path), [{"imdb_id": "tt1"},
                                       {"imdb_id": "tt2"}])
    with open(path, "a", encoding="utf-8") as fh:
        fh.write('{"imdb_id": "tt3"')        # line cut by an interruption
    assert fetch_wikipedia.already_done(str(path)) == {"tt1", "tt2"}
    assert json.loads(path.read_text().splitlines()[0]) == {"imdb_id": "tt1"}


def test_title_from_url():
    assert fetch_wikipedia.title_from_url(
        "https://en.wikipedia.org/wiki/Am%C3%A9lie_(film)") == "Amélie (film)"
