"""Shared pytest fixtures: a local Spark session and a tiny IMDb sample.

The sample is hand written to contain the data quality problems that the
preparation step must detect. It is only used by the tests.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from imdb.common import RAW_TABLES  # noqa: E402

N = "\\N"

SAMPLE = {
    "name.basics": [
        ["nm1", "Alice Actor", "1950", N, "actress,director", "tt1,tt2"],
        ["nm2", "Bob Director", "1940", "2010", "director,writer", "tt1"],
        ["nm3", "Dead Before Born", "2005", "1980", "actor", "tt999"],
        ["nm4", "", "1960", N, N, N],
        ["nm4", "Duplicate", "1960", N, N, N],
    ],
    "title.basics": [
        ["tt1", "movie", "Film One", "Film One", "0", "1990", N, "100",
         "Drama,Comedy"],
        ["tt2", "movie", "Film Two", "Le Film Deux", "0", "2000", N, "0",
         "Drama"],
        ["tt3", "tvSeries", "Show", "Show", "0", "2005", "2001", N,
         "Drama"],
        ["tt4", "tvEpisode", "Ep 1", "Ep 1", "5", "2005", N, "30", N],
    ],
    "title.akas": [
        ["tt1", "1", "Film One", "US", "en", "imdbDisplay", N, "0"],
        ["tt2", "1", "Le Film Deux", "FR", N, N, N, "1"],
        ["tt999", "1", "Ghost", N, N, N, N, "1"],
    ],
    "title.crew": [
        ["tt1", "nm2", "nm2,nm404"],
        ["tt2", "nm1", N],
    ],
    "title.episode": [
        ["tt4", "tt3", "1", "1"],
        ["tt5", "tt3", N, N],
    ],
    "title.principals": [
        ["tt1", "1", "nm1", "actress", N, '["Jane"]'],
        ["tt1", "2", "nm2", "director", N, N],
        ["tt2", "1", "nm3", "actor", N, '["Kid"]'],
        ["tt2", "2", "nm404", "actor", N, N],
    ],
    "title.ratings": [
        ["tt1", "8.1", "1500"],
        ["tt2", "11.0", "10"],
        ["tt999", "5.0", "3"],
    ],
}


@pytest.fixture(scope="session")
def spark():
    from pyspark.sql import SparkSession
    session = (
        SparkSession.builder.master("local[2]")
        .appName("imdb-tests")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    yield session
    session.stop()


def write_sample(directory, sample):
    os.makedirs(directory, exist_ok=True)
    for table, rows in sample.items():
        path = os.path.join(directory, f"{table}.tsv")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\t".join(RAW_TABLES[table]) + "\n")
            for row in rows:
                fh.write("\t".join(row) + "\n")


@pytest.fixture(scope="session")
def raw_dir(tmp_path_factory):
    directory = str(tmp_path_factory.mktemp("raw"))
    write_sample(directory, SAMPLE)
    return directory
