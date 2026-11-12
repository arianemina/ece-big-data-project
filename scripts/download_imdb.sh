#!/usr/bin/env bash
# Download the IMDb non-commercial datasets into data/raw/.
# Usage: scripts/download_imdb.sh [table ...]   (default: all seven tables)
# Example (only what enrichment/streaming need):
#   scripts/download_imdb.sh title.basics title.ratings title.principals name.basics
set -euo pipefail

BASE_URL="https://datasets.imdbws.com"
DEST="$(cd "$(dirname "$0")/.." && pwd)/data/raw"
ALL_TABLES=(name.basics title.akas title.basics title.crew title.episode title.principals title.ratings)

tables=("$@")
if [ ${#tables[@]} -eq 0 ]; then
  tables=("${ALL_TABLES[@]}")
fi

mkdir -p "$DEST"
for t in "${tables[@]}"; do
  file="$t.tsv.gz"
  echo "Downloading $file ..."
  if [ -f "$DEST/$file" ] && gzip -t "$DEST/$file" 2>/dev/null; then
    echo "  already present and valid, skipping"
    continue
  fi
  # Download to a temporary file so an interrupted transfer never leaves a
  # truncated archive behind.
  curl -fL --retry 3 -o "$DEST/$file.part" "$BASE_URL/$file"
  mv "$DEST/$file.part" "$DEST/$file"
done
echo "Done. Files are in $DEST"
