#!/usr/bin/env bash
# Run the whole data enrichment step (run the preparation step first).
# The gathering script is resumable: re-run this script after an
# interruption and only the missing pages are downloaded.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="src${PYTHONPATH:+:${PYTHONPATH}}"

python -m imdb.enrichment.select_targets
python -m imdb.enrichment.fetch_wikipedia
python -m imdb.enrichment.build_enriched
