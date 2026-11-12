#!/usr/bin/env bash
# Download the IMDb non-commercial datasets into data/raw.
# Usage: scripts/download_imdb.sh [target_dir]
set -euo pipefail

TARGET_DIR="${1:-data/raw}"
BASE_URL="https://datasets.imdbws.com"
FILES=(
  name.basics
  title.akas
  title.basics
  title.crew
  title.episode
  title.principals
  title.ratings
)

mkdir -p "${TARGET_DIR}"
for name in "${FILES[@]}"; do
  file="${name}.tsv.gz"
  if [[ -s "${TARGET_DIR}/${file}" ]]; then
    echo "Already present: ${file}"
    continue
  fi
  echo "Downloading ${file}"
  curl --fail --location --retry 3 --output "${TARGET_DIR}/${file}.part" \
    "${BASE_URL}/${file}"
  mv "${TARGET_DIR}/${file}.part" "${TARGET_DIR}/${file}"
done
echo "IMDb files are in ${TARGET_DIR}"
