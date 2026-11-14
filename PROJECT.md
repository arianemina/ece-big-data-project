# Project guide

## Contributors

| Name | GitHub | Email |
| --- | --- | --- |
| Lisa | Lisa7577 | l.elgabteni7@gmail.com |
| Ariane | arianemina | ariane.mina@yahoo.com |

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

### Alternative: Docker (also starts Kafka)

The streaming part needs a Kafka broker, which is provided by
`docker-compose.yml`. The same file starts a `spark` container with Python
3.12, Java 17 and the pinned `requirements.txt`, so nothing but Docker is
needed on the host (useful when the local Java version is not supported by
Spark).

```bash
docker compose up -d --build        # Kafka + spark container
docker compose exec spark scripts/run_preparation.sh
```

Every `python -m ...` or `scripts/...` command of this guide can be run in
the container by prefixing it with `docker compose exec spark`. The
container reads and writes the repository folder, so `data/` and `output/`
are shared with the host. The default driver memory in the container is
2 GB (Docker Desktop with 4 GB); set `SPARK_DRIVER_MEMORY` before
`docker compose up` to change it. Stop everything with `docker compose down`;
`docker compose down -v` also deletes the Spark temporary files (they can
take several GB after a job that crashed) and the Spark packages cache.

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

## Data enrichment

Run after the preparation step (it reads the cleaned tables):

```bash
scripts/run_enrichment.sh
```

This runs, in order:

1. `imdb.enrichment.select_targets` (Spark): feature-length movies released
   1980-2025, top 10 per (year, genre) by number of votes, and the first 3
   principals of each selected film (IMDb billing order).
2. `imdb.enrichment.fetch_wikipedia` (plain Python, outside Spark): maps the
   IMDb IDs to Wikidata items and English Wikipedia articles (Wikidata
   property P345), then downloads the film articles (plain text) and the
   lead sections of the principals. Requests are sent one at a time below
   the Wikimedia limit (about 170 per minute, `Retry-After` and `maxlag`
   honoured) with a User-Agent containing a contact URL. The raw answers are
   appended to `data/enrichment/raw/*.jsonl`; the script is resumable. A full
   run takes about 1 hour (`--limit 50` for a quick test).
3. `imdb.enrichment.build_enriched` (Spark): schema enforcement, plot
   section extraction, text cleaning, joins with IMDb, `lineage` column
   (source permalink, Wikidata URI, revision, retrieval time, license) and
   `enrichment_note` when information is missing.

Enriched datasets: `data/enrichment/enriched/films` (partitioned by year)
and `data/enrichment/enriched/principals`. Report tables:
`output/enrichment`.

| Variable | Default | Meaning |
| --- | --- | --- |
| `FIRST_YEAR`, `LAST_YEAR` | 1980, 2025 | release years |
| `ENRICH_TOP_N` | 10 | films per (year, genre), 0 = all |
| `ENRICH_PRINCIPALS` | 3 | principals per film, 0 = all |
| `WIKI_USER_AGENT` | project URL | User-Agent sent to Wikimedia |

## Streaming data processing

TODO

## Tests

```bash
pytest
```

The tests run on a small hand written sample and do not need the IMDb files.

## AI tools used

| Tool | Used by | Tasks |
| --- | --- | --- |
| Claude Code (Anthropic) | Ariane | Code of the Docker/Kafka environment, the data enrichment pipeline, the streaming pipeline and their tests |
| TODO | Lisa | TODO |

The methodological explanations and reasoning in `REPORT.md` were written
by the group members without AI tools.
