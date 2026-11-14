"""Tests for the open question on small DataFrames (no network)."""

from imdb.open_question import fetch_birth_countries as fb
from imdb.open_question import foreign_born as fo


def countries(spark, rows):
    return spark.createDataFrame(
        [(q, "p", c, iso, lbl, "s", "t") for q, c, iso, lbl in rows],
        fo.COUNTRY_SCHEMA)


def test_birth_country_rules(spark):
    df = countries(spark, [
        ("Q1", "c_us", "US", "United States"),
        ("Q2", "c_su", "SU", "Soviet Union"),       # historical state ...
        ("Q2", "c_ua", "UA", "Ukraine"),            # ... current one wins
        ("Q3", "c_rs", "RS", "Serbia"),             # two current states:
        ("Q3", "c_xk", "XK", "Kosovo"),             # ambiguous
        ("Q4", None, None, None),                   # place without country
    ])
    got = {r.wikidata_id: (r.country_iso, r.ambiguous_country)
           for r in fo.birth_country(df).collect()}
    assert got == {"Q1": ("US", False), "Q2": ("UA", False),
                   "Q3": ("RS", True)}


def test_born_abroad_and_shares(spark):
    principals = spark.createDataFrame(
        [("tt1", "nm1", "actor"), ("tt1", "nm2", "director"),
         ("tt1", "nm3", "actress"), ("tt2", "nm4", "actor")],
        "tconst STRING, nconst STRING, category STRING")
    links = spark.createDataFrame(
        [("nm1", "person", "http://www.wikidata.org/entity/Q1"),
         ("nm2", "person", "http://www.wikidata.org/entity/Q2"),
         ("nm3", "person", None)], fo.LINK_SCHEMA)
    cty = countries(spark, [("Q1", "c_us", "US", "United States"),
                            ("Q2", "c_gb", "GB", "United Kingdom")])
    people = fo.principals_with_country(principals, links, cty, home="US")
    flags = {r.nconst: (r.born_abroad, r.role) for r in people.collect()}
    assert flags == {"nm1": (False, "cast"), "nm2": (True, "crew"),
                     "nm3": (None, "cast"), "nm4": (None, "cast")}
    row = fo.share(people, "tconst").where("tconst = 'tt1'").first()
    assert (row.principals, row.known_country, row.born_abroad,
            row.pct_born_abroad) == (3, 2, 1, 50.0)


def test_film_profiles(spark):
    people = spark.createDataFrame(
        [("tt1", False), ("tt1", False), ("tt2", True), ("tt2", False),
         ("tt3", True), ("tt3", True), ("tt4", True), ("tt4", None)],
        "tconst STRING, born_abroad BOOLEAN")
    films = spark.createDataFrame(
        [(t, 2000, 7.0, 1000) for t in ("tt1", "tt2", "tt3", "tt4")],
        "tconst STRING, year INT, averageRating DOUBLE, numVotes INT")
    got = {r.tconst: r.profile
           for r in fo.film_profiles(films, people, 2).collect()}
    # tt4 has only one known country: left out
    assert got == {"tt1": "us_only", "tt2": "mixed", "tt3": "abroad_only"}


def test_period_buckets(spark):
    df = spark.createDataFrame([(1980,), (1984,), (1985,), (2025,)],
                               "year INT")
    got = [r.period for r in fo.with_period(df, width=5).collect()]
    assert got == ["1980-1984", "1980-1984", "1985-1989", "2025-2025"]


def test_items_without_place_get_an_empty_record():
    recs = fb.to_records(["Q1", "Q2"], [{
        "item": {"value": "http://www.wikidata.org/entity/Q1"},
        "place": {"value": "http://www.wikidata.org/entity/Q60"},
        "country": {"value": "http://www.wikidata.org/entity/Q30"},
        "iso": {"value": "US"},
        "countryLabel": {"value": "United States"}}], "t")
    assert [(r["wikidata_id"], r["country_iso"]) for r in recs] == [
        ("Q1", "US"), ("Q2", None)]
