"""Paths and parameters of the streaming pipeline."""
import os

from src.common.imdb import DATA_DIR

STREAM_DIR = os.path.join(DATA_DIR, "streaming")
REFERENCE = os.path.join(STREAM_DIR, "reference")
OUTPUT_DIR = os.path.join(STREAM_DIR, "output")
CHECKPOINT_DIR = os.path.join(STREAM_DIR, "checkpoints")
METRICS_FILE = os.path.join(STREAM_DIR, "metrics", "progress.jsonl")

MATCHED_EVENTS = os.path.join(OUTPUT_DIR, "matched_events")
ENTITY_WINDOWS = os.path.join(OUTPUT_DIR, "entity_windows")
TRAFFIC_WINDOWS = os.path.join(OUTPUT_DIR, "traffic_windows")

# Optional input: output of the enrichment pipeline (exact article titles)
ENRICHED_FILMS = os.path.join(DATA_DIR, "enrichment", "output", "films")
ENRICHED_PRINCIPALS = os.path.join(DATA_DIR, "enrichment", "output",
                                   "principals")

EVENTSTREAMS_URL = "https://stream.wikimedia.org/v2/stream/recentchange"
KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9094")
TOPIC = "wikipedia.recentchange"

WIKIS = ["enwiki"]            # wikis kept by the Spark filter
WINDOW = "5 minutes"          # aggregation window (event time)
WATERMARK = "10 minutes"      # accepted lateness before state is finalised
TRIGGER = "30 seconds"        # micro-batch interval
MIN_VOTES = 5000              # popularity threshold for reference titles
