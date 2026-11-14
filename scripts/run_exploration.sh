#!/usr/bin/env bash
# Run every exploration query on the cleaned tables (run preparation first).
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="src${PYTHONPATH:+:${PYTHONPATH}}"

for query in q1_runtime_outliers q2_q3_top_genres q4_directors \
             q5_tv_series q6_multilingual_actors q7_early_peak \
             q8_multi_talented; do
  echo "=== ${query}"
  python -m "imdb.exploration.${query}"
done
