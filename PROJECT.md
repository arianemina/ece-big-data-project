# Project guide

## Contributors

| Name | GitHub | Email |
| --- | --- | --- |
| Lisa | Lisa7577 | TODO |
| Ariane | arianemina | TODO |

## Requirements

- Python 3.10 or newer
- Java 17 or 21 (required by Spark 4)
- About 15 GB of free disk space and 8 GB of RAM for the full IMDb dataset

## Setup

```bash
git clone https://github.com/arianemina/ece-big-data-project.git
cd ece-big-data-project
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Spark memory can be tuned with environment variables, for example
`export SPARK_DRIVER_MEMORY=6g` on a machine with less RAM.

## Data download

```bash
scripts/download_imdb.sh            # writes the 7 IMDb files to data/raw
```

## Data preparation

```bash
scripts/run_preparation.sh
```

This runs, in order:

1. `imdb.preparation.null_profile`: percentage of null, `\N` or empty values
   for every column, and the five most incomplete columns.
2. `imdb.preparation.quality_checks`: data quality checks (impossible dates,
   orphan foreign keys, duplicates, out of range values).
3. `imdb.preparation.clean`: applies the handling rules and writes cleaned
   Parquet tables to `data/clean`.

Results are written to `output/preparation` as CSV files and Markdown
previews.

## Tests

```bash
pytest
```

The tests run on a small hand written sample and do not need the IMDb files.

## AI tools used

TODO
