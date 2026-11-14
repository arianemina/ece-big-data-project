"""Paths and parameters of the streaming pipeline."""

import os

DATA_DIR = os.environ.get("IMDB_DATA_DIR", "data")
STREAM_DIR = os.path.join(DATA_DIR, "streaming")
REFERENCE = os.path.join(STREAM_DIR, "reference")
SINK_DIR = os.path.join(STREAM_DIR, "sinks")
CHECKPOINT_DIR = os.path.join(STREAM_DIR, "checkpoints")
METRICS_FILE = os.path.join(STREAM_DIR, "metrics", "progress.jsonl")

MATCHED_EVENTS = os.path.join(SINK_DIR, "matched_events")
ENTITY_WINDOWS = os.path.join(SINK_DIR, "entity_windows")
TRAFFIC_WINDOWS = os.path.join(SINK_DIR, "traffic_windows")

SECTION = "streaming"   # report tables go to output/streaming

# Optional input: output of the enrichment step (exact article titles).
ENRICHED_FILMS = os.path.join(DATA_DIR, "enrichment", "enriched", "films")
ENRICHED_PRINCIPALS = os.path.join(DATA_DIR, "enrichment", "enriched",
                                   "principals")

EVENTSTREAMS_URL = "https://stream.wikimedia.org/v2/stream/recentchange"
KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9094")
TOPIC = "wikipedia.recentchange"

WIKIS = ["enwiki"]            # wikis kept by the Spark filter
WINDOW = "5 minutes"          # aggregation window (event time)
WATERMARK = "10 minutes"      # accepted lateness before state is finalised
TRIGGER = "30 seconds"        # micro-batch interval
MIN_VOTES = int(os.environ.get("STREAM_MIN_VOTES", "5000"))
