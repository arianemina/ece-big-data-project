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
are shared with the host.

In the container, `SPARK_DRIVER_MEMORY` defaults to `2g` and
`SPARK_SHUFFLE_PARTITIONS` to `16`, sized for Docker Desktop with 4 GB of
memory. They replace the local defaults; export them before
`docker compose up` to change them (for example `SPARK_DRIVER_MEMORY=4g`
with 8 GB given to Docker).

The first streaming run downloads the Spark Kafka connector
(`spark-sql-kafka`) from Maven Central, so it needs internet access and
takes a minute longer; the `ivy-cache` volume keeps it for later runs.

Stop everything with `docker compose down`;
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

TODO

## Streaming data processing

Needs Kafka, so run it with Docker (`docker compose up -d --build`), after
the preparation step. If the enrichment output exists, its exact Wikipedia
article titles are used for matching as well.

1. Build the IMDb lookup table used to filter the stream (Spark):

   ```bash
   docker compose exec spark python -m imdb.streaming.build_reference
   ```

2. In a first terminal, start the Structured Streaming job (it stops by
   itself after `--duration-minutes`, 20 by default):

   ```bash
   docker compose exec spark python -m imdb.streaming.stream_processor --duration-minutes 25
   ```

3. In a second terminal, start the producer that forwards the Wikimedia
   EventStreams `recentchange` feed to the Kafka topic
   `wikipedia.recentchange`:

   ```bash
   docker compose exec spark python -m imdb.streaming.producer --duration-minutes 22
   ```

4. Optional, to test late data: while the job runs, replay events from 30
   minutes ago (older than the 10-minute watermark):

   ```bash
   docker compose exec spark python -m imdb.streaming.producer --since-minutes 30 --max-events 3000
   ```

5. When the job has stopped, write the result tables to `output/streaming`:

   ```bash
   docker compose exec spark python -m imdb.streaming.summarize
   ```

The windowed sinks are written in append mode: a 5-minute window is only
emitted once the watermark (max event time - 10 minutes) has passed its
end, so the last ~15 minutes of a run never reach `entity_windows` and
`traffic_windows`. `summarize` recounts the windows in batch from
`matched_events` (table `window_reconciliation`) to show them.

Sinks (Parquet): `data/streaming/sinks/` (`matched_events`,
`entity_windows`, `traffic_windows`); per-batch metrics:
`data/streaming/metrics/progress.jsonl`. To start again from a clean state,
delete `data/streaming/checkpoints`, `data/streaming/sinks` and
`data/streaming/metrics`.

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
