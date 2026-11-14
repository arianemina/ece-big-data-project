"""Paths and parameters of the open question (birth countries)."""

import os

from imdb.enrichment import config as E

OQ_DIR = os.path.join(E.DATA_DIR, "open_question")
RAW_COUNTRIES = os.path.join(OQ_DIR, "raw", "birth_countries.jsonl")
SECTION = "open_question"      # report tables go to output/open_question

HOME_COUNTRY = os.environ.get("OQ_HOME_COUNTRY", "US")   # ISO 3166 alpha-2
PERIOD_YEARS = 5               # width of the time buckets
MIN_KNOWN_PRINCIPALS = 2       # film profile needs 2+ known countries
