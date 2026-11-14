"""Paths and default parameters of the enrichment pipeline."""

import os

DATA_DIR = os.environ.get("IMDB_DATA_DIR", "data")
ENRICH_DIR = os.path.join(DATA_DIR, "enrichment")
TARGETS_DIR = os.path.join(ENRICH_DIR, "targets")
RAW_DIR = os.path.join(ENRICH_DIR, "raw")
ENRICHED_DIR = os.path.join(ENRICH_DIR, "enriched")

TARGET_FILMS = os.path.join(TARGETS_DIR, "films")
TARGET_PRINCIPALS = os.path.join(TARGETS_DIR, "principals")
TARGET_FILM_IDS = os.path.join(TARGETS_DIR, "film_ids")
TARGET_PERSON_IDS = os.path.join(TARGETS_DIR, "person_ids")

RAW_LINKS = os.path.join(RAW_DIR, "wikidata_links.jsonl")
RAW_FILM_PAGES = os.path.join(RAW_DIR, "wikipedia_films.jsonl")
RAW_PERSON_PAGES = os.path.join(RAW_DIR, "wikipedia_people.jsonl")

ENRICHED_FILMS = os.path.join(ENRICHED_DIR, "films")
ENRICHED_PRINCIPALS = os.path.join(ENRICHED_DIR, "principals")

SECTION = "enrichment"   # report tables go to output/enrichment

# Selection defaults (see imdb.enrichment.select_targets). The feature film
# rule (runtime > 40 min) comes from imdb.exploration.base.
FIRST_YEAR = int(os.environ.get("FIRST_YEAR", "1980"))
LAST_YEAR = int(os.environ.get("LAST_YEAR", "2025"))
TOP_N = int(os.environ.get("ENRICH_TOP_N", "10"))
N_PRINCIPALS = int(os.environ.get("ENRICH_PRINCIPALS", "3"))

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
CONTENT_LICENSE = "CC BY-SA 4.0"
