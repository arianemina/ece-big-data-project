"""Paths and default parameters of the enrichment pipeline."""
import os

from src.common.imdb import DATA_DIR

ENRICH_DIR = os.path.join(DATA_DIR, "enrichment")
TARGETS_DIR = os.path.join(ENRICH_DIR, "targets")
RAW_DIR = os.path.join(ENRICH_DIR, "raw")
OUTPUT_DIR = os.path.join(ENRICH_DIR, "output")

TARGET_FILMS = os.path.join(TARGETS_DIR, "films")
TARGET_PRINCIPALS = os.path.join(TARGETS_DIR, "principals")
TARGET_FILM_IDS = os.path.join(TARGETS_DIR, "film_ids")
TARGET_PERSON_IDS = os.path.join(TARGETS_DIR, "person_ids")

RAW_LINKS = os.path.join(RAW_DIR, "wikidata_links.jsonl")
RAW_FILM_PAGES = os.path.join(RAW_DIR, "wikipedia_films.jsonl")
RAW_PERSON_PAGES = os.path.join(RAW_DIR, "wikipedia_people.jsonl")

ENRICHED_FILMS = os.path.join(OUTPUT_DIR, "films")
ENRICHED_PRINCIPALS = os.path.join(OUTPUT_DIR, "principals")
COVERAGE = os.path.join(OUTPUT_DIR, "coverage")

# Selection defaults (see src.enrichment.select_targets)
YEAR_FROM = 1980
YEAR_TO = 2025
MIN_RUNTIME = 40      # feature film: running time of 40 minutes or more
TOP_N = 10            # films per (year, genre)
N_PRINCIPALS = 3      # principals per film

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
CONTENT_LICENSE = "CC BY-SA 4.0"
