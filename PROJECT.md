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

## Data exploration

Run after the preparation step:

```bash
scripts/run_exploration.sh
```

| Script | Question |
| --- | --- |
| `q1_runtime_outliers` | Feature-length movies whose runtime is far from their genre average |
| `q2_q3_top_genres` | Top 3 genres per year (1980-2025) and comparison with the other genres |
| `q4_directors` | Directors with one movie rated 8+ and several movies rated 6 or less |
| `q5_tv_series` | Series whose worst episode is in the last season and best in the first two |
| `q6_multilingual_actors` | Actors successful in films of 2+ and 3+ original languages |
| `q7_early_peak` | Actors with 20+ year careers and 15+ movies who peaked early |
| `q8_multi_talented` | Actor / director / writer profiles and their multi-role performance |

Thresholds (minimum votes, z-score, success rating) can be changed with the
environment variables listed at the top of each script. Results go to
`output/exploration`.

## Tests

```bash
pytest
```

The tests run on a small hand written sample and do not need the IMDb files.

## AI tools used

TODO
