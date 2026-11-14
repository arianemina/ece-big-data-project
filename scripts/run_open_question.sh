#!/usr/bin/env bash
# Open question: birth countries of the principals of the most popular films.
# Run after the enrichment step (it reuses its targets and Wikidata links).
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="src${PYTHONPATH:+:${PYTHONPATH}}"

python -m imdb.open_question.fetch_birth_countries
python -m imdb.open_question.foreign_born
