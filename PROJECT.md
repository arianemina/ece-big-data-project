# ECE Big Data Processing Project — Execution and Operations Guide

## Contributors

| Name  | GitHub      | Email                  |
| ----- | ----------- | ---------------------- |
| Lisa  | Lisa7577    | l.elgabteni7@gmail.com |
| Ariane | arianemina | ariane.mina@yahoo.com  |

Group: gr-01

## Repository layout

```text
.
├── docker-compose.yml      # Kafka (KRaft) + Spark/Python runtime
├── Dockerfile              # Spark 4.2.0 / Python 3.13 / Java 21 image
├── requirements.txt        # extra Python dependencies
├── scripts/
│   └── download_imdb.sh    # downloads the IMDb TSV files into data/raw
├── src/
│   ├── common/             # SparkSession factory, IMDb schemas and readers
│   ├── ingest_imdb.py      # TSV.gz -> Parquet conversion
│   ├── enrichment/         # Wikipedia enrichment pipeline
│   └── streaming/          # Wikipedia change events -> Kafka -> Spark
├── data/                   # generated, never committed
├── PROJECT.md
└── REPORT.md
```

## Requirements

- Docker Desktop (or Docker Engine) with Docker Compose v2
- At least 4 GB of memory allocated to Docker
- About 15 GB of free disk space (raw files, Parquet files and outputs)
- An internet connection (IMDb download, Wikipedia/Wikidata APIs,
  Wikimedia EventStreams)

Nothing else needs to be installed on the host: Spark, Java and Python run
inside the `spark` container.

## Setup from scratch

1. Clone the repository and enter it:

   ```bash
   git clone https://github.com/arianemina/ece-big-data-project.git
   cd ece-big-data-project
   ```

2. Download the IMDb datasets (about 2 GB, into `data/raw/`):

   ```bash
   scripts/download_imdb.sh
   ```

3. Build the image and start the stack (Kafka + Spark container):

   ```bash
   docker compose up -d --build
   ```

   JupyterLab is available at <http://localhost:8888> and the Spark UI of a
   running job at <http://localhost:4040>.

4. Convert the raw files to Parquet with explicit schemas (once):

   ```bash
   docker compose exec spark python -m src.ingest_imdb
   ```

   Output: `data/parquet/<table>/`.

All the following commands are run from the repository root on the host.

## 1. Data preparation

_To be completed._

## 2. Data exploration

_To be completed._

## 3. Data enrichment

Prerequisite: `title.basics`, `title.ratings`, `title.principals` and
`name.basics` converted to Parquet (setup step 4).

1. Select the films and principals to enrich (Spark): feature films
   (>= 40 min) released 1980-2025, top 10 per (year, genre) by number of
   votes, first 3 principals of each film:

   ```bash
   docker compose exec spark python -m src.enrichment.select_targets
   ```

   Parameters: `--year-from`, `--year-to`, `--min-runtime`, `--top-n`,
   `--principals` (`--top-n 0 --principals 0` = full dataset).

2. Gather the raw data from Wikidata and English Wikipedia (plain Python,
   rate limited, resumable — simply re-run it after an interruption):

   ```bash
   docker compose exec spark python -m src.enrichment.fetch_wikipedia
   ```

   Use `--limit 50` for a quick test. A full run takes about 1 hour.
   Raw API answers are stored in `data/enrichment/raw/*.jsonl`.

3. Clean, enforce the schema, add the lineage and join with IMDb (Spark):

   ```bash
   docker compose exec spark python -m src.enrichment.build_enriched
   ```

   Outputs in `data/enrichment/output/`: `films/` (synopses, partitioned
   by year), `principals/` (biographies) and `coverage/` (CSV summary).

## 4. Streaming data processing

_To be completed._

## 5. Open question

_To be completed._

## Stopping and cleaning up

```bash
docker compose down          # stop containers
docker compose down -v       # also delete the Ivy (Spark packages) cache
rm -rf data/                 # delete all downloaded and generated data
```

## Use of AI / LLM tools

- **Tool:** Claude Code (Anthropic)
- **Used for (code only):** setting up the Docker/Kafka/Spark environment,
  writing the IMDb ingestion code, the Wikipedia enrichment pipeline and the
  streaming pipeline.
- **Not used for:** the explanations, reasoning and methodology write-ups in
  `REPORT.md`, which were written by the group members.
