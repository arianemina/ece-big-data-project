#!/usr/bin/env bash
# Run the whole data preparation step on the raw IMDb files.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="src${PYTHONPATH:+:${PYTHONPATH}}"

python -m imdb.preparation.null_profile
python -m imdb.preparation.quality_checks
python -m imdb.preparation.clean
