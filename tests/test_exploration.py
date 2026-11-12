"""Tests for the exploration queries on small cleaned tables."""

import os

import pytest

import imdb.common as common
from imdb.exploration import (q1_runtime_outliers, q2_q3_top_genres,
                              q4_directors, q5_tv_series,
                              q6_multilingual_actors, q7_early_peak,
                              q8_multi_talented)
from imdb.exploration.base import feature_movies
from imdb.exploration.languages import original_languages

BASICS = ("tconst STRING, titleType STRING, primaryTitle STRING, "
          "originalTitle STRING, isAdult INT, startYear INT, endYear INT, "
          "runtimeMinutes INT, genres ARRAY<STRING>")


def movie(tconst, year, runtime, genres, title=None):
    title = title or tconst
    return (tconst, "movie", title, title, 0, year, None, runtime, genres)


@pytest.fixture()
def clean_dir(spark, tmp_path, monkeypatch):
    """Write a small cleaned dataset and point read_clean to it."""
    basics, ratings, crew, principals, episodes, akas = [], [], [], [], [], []
    names = [("nm_dir", "One Hit"), ("nm_actor", "Long Career"),
             ("nm_multi", "Multi Talent"), ("nm_poly", "Polyglot")]

    # Director: one movie rated 8.5, three rated <= 6.
    for i, rating in enumerate([8.5, 5.0, 6.0, 4.0, 7.0]):
        tconst = f"ttd{i}"
        basics.append(movie(tconst, 1990 + i, 100, ["Drama"]))
        ratings.append((tconst, rating, 1000))
        crew.append((tconst, ["nm_dir"], None))

    # Actor: 16 movies over 30 years, best movies early.
    for i in range(16):
        tconst = f"tta{i}"
        basics.append(movie(tconst, 1980 + 2 * i, 95, ["Comedy"]))
        ratings.append((tconst, 9.0 - 0.3 * i, 500))
        principals.append((tconst, 1, "nm_actor", "actor"))

    # Multi-talented: directs and acts, sometimes both on the same movie.
    for i in range(4):
        tconst = f"ttm{i}"
        basics.append(movie(tconst, 2000 + i, 110, ["Action"]))
        ratings.append((tconst, 6.0 + i, 2000))
        crew.append((tconst, ["nm_multi"], None))
        principals.append((tconst, 1, "nm_multi", "director"))
    for i in range(3):
        tconst = f"ttn{i}"
        basics.append(movie(tconst, 2010 + i, 110, ["Action"]))
        ratings.append((tconst, 5.0, 2000))
        principals.append((tconst, 1, "nm_multi", "actor"))
    principals.append(("ttm3", 2, "nm_multi", "actor"))

    # Polyglot: successful films in French, German and English.
    for tconst, region, title in [("ttf", "FR", "Le Film"),
                                  ("ttg", "DE", "Der Film"),
                                  ("tte", "US", "The Film")]:
        basics.append(movie(tconst, 2005, 120, ["Drama"], title))
        ratings.append((tconst, 8.0, 10000))
        principals.append((tconst, 1, "nm_poly", "actress"))
        akas.append((tconst, 1, title, region, None, 1))
        akas.append((tconst, 2, "Translated", "XX", None, 0))

    # A very long drama and a short film that is not feature length.
    basics.append(movie("ttlong", 2001, 900, ["Drama"]))
    basics.append(movie("ttshort", 2001, 20, ["Drama"]))

    # TV series: 3 seasons of 10 episodes, best in S1, worst in S3.
    basics.append(("tts", "tvSeries", "Show", "Show", 0, 2000, 2003, None,
                   ["Drama"]))
    for season in (1, 2, 3):
        for ep in range(1, 11):
            tconst = f"tts{season}e{ep}"
            basics.append((tconst, "tvEpisode", tconst, tconst, 0, 2000,
                           None, 40, ["Drama"]))
            episodes.append((tconst, "tts", season, ep))
            rating = 7.0
            if (season, ep) == (1, 3):
                rating = 9.5
            if (season, ep) == (3, 10):
                rating = 3.0
            ratings.append((tconst, rating, 100))

    tables = {
        "title_basics": (basics, BASICS),
        "title_ratings": (ratings, "tconst STRING, averageRating DOUBLE, "
                                   "numVotes INT"),
        "title_crew": (crew, "tconst STRING, directors ARRAY<STRING>, "
                             "writers ARRAY<STRING>"),
        "title_principals": (principals, "tconst STRING, ordering INT, "
                                         "nconst STRING, category STRING"),
        "title_episode": (episodes, "tconst STRING, parentTconst STRING, "
                                    "seasonNumber INT, episodeNumber INT"),
        "title_akas": (akas, "tconst STRING, ordering INT, title STRING, "
                             "region STRING, language STRING, "
                             "isOriginalTitle INT"),
        "name_basics": (names, "nconst STRING, primaryName STRING"),
    }
    for name, (rows, schema) in tables.items():
        spark.createDataFrame(rows, schema).write.mode("overwrite") \
            .parquet(os.path.join(str(tmp_path), name))
    monkeypatch.setattr(common, "CLEAN_DIR", str(tmp_path))
    return str(tmp_path)


def test_feature_movies_excludes_short_films(spark, clean_dir):
    ids = {r.tconst for r in feature_movies(spark).collect()}
    assert "ttshort" not in ids
    assert "tts" not in ids


def test_q1_finds_very_long_movie(spark, clean_dir):
    outliers = q1_runtime_outliers.runtime_outliers(
        feature_movies(spark), z_threshold=2)
    ids = {(r.tconst, r.direction) for r in outliers.collect()}
    assert ("ttlong", "longer") in ids


def test_q2_ranks_genres_by_votes(spark, clean_dir):
    popularity = q2_q3_top_genres.genre_year_popularity(
        spark, feature_movies(spark))
    top_2005 = [r.genre for r in q2_q3_top_genres.top_genres(popularity)
                .where("year = 2005").collect()]
    assert top_2005 == ["Drama"]
    comparison = q2_q3_top_genres.top_vs_rest(popularity).collect()
    assert comparison


def test_q4_one_hit_director(spark, clean_dir):
    rows = q4_directors.one_hit_directors(spark, min_votes=0).collect()
    assert [r.nconst for r in rows] == ["nm_dir"]
    assert rows[0].movies_rated_6_or_less == 3
    assert rows[0].hit_rating == 8.5


def test_q5_series(spark, clean_dir):
    rows = q5_tv_series.qualifying_series(spark, min_votes=0).collect()
    assert [r.series_tconst for r in rows] == ["tts"]
    assert rows[0].best_season == 1 and rows[0].worst_season == 3


def test_q6_languages(spark, clean_dir):
    langs = {r.tconst: r.original_language
             for r in original_languages(spark).collect()}
    assert langs == {"ttf": "fr", "ttg": "de", "tte": "en"}
    rows = q6_multilingual_actors.multilingual_actors(spark, 3).collect()
    assert [r.nconst for r in rows] == ["nm_poly"]


def test_q7_early_peak(spark, clean_dir):
    rows = q7_early_peak.early_peak_actors(spark, min_votes=0).collect()
    assert [r.nconst for r in rows] == ["nm_actor"]
    assert rows[0].career_years == 30


def test_q8_multi_talented(spark, clean_dir):
    person_movies = q8_multi_talented.roles_per_movie(spark, min_votes=0)
    talented = q8_multi_talented.multi_talented(person_movies)
    assert [r.nconst for r in talented.collect()] == ["nm_multi"]
    per_person, combos = q8_multi_talented.performance(person_movies,
                                                       talented)
    row = per_person.collect()[0]
    assert row.multiple_roles_movies == 1
    assert row.multiple_roles_avg_rating == 9.0
