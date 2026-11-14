"""Summarise the sinks and metrics of a streaming run (Spark batch).

Writes CSV files and Markdown previews to ``output/streaming`` for REPORT.md.

Usage: python -m imdb.streaming.summarize
"""

import json
import os

from pyspark.sql import functions as F

from imdb.common import get_spark, write_output
from imdb.streaming import config as C


def progress_metrics(path):
    """Aggregate the StreamingQueryProgress reports per query."""
    stats = {}
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            p = json.loads(line)
            s = stats.setdefault(p["name"], {
                "query": p["name"], "batches": 0, "input_rows": 0,
                "avg_input_rows_per_s": [], "max_processed_rows_per_s": 0.0,
                "avg_batch_ms": [], "max_batch_ms": 0,
                "rows_dropped_by_watermark": 0, "last_watermark": "",
            })
            s["batches"] += 1
            s["input_rows"] += p.get("numInputRows", 0)
            s["avg_input_rows_per_s"].append(
                p.get("inputRowsPerSecond") or 0.0)
            s["max_processed_rows_per_s"] = max(
                s["max_processed_rows_per_s"],
                p.get("processedRowsPerSecond") or 0.0)
            duration = p.get("durationMs", {}).get("triggerExecution", 0)
            s["avg_batch_ms"].append(duration)
            s["max_batch_ms"] = max(s["max_batch_ms"], duration)
            for op in p.get("stateOperators", []):
                # cumulative counter: keep the last (largest) value
                s["rows_dropped_by_watermark"] = max(
                    s["rows_dropped_by_watermark"],
                    op.get("numRowsDroppedByWatermark", 0))
            watermark = p.get("eventTime", {}).get("watermark")
            if watermark and not watermark.startswith("1970"):
                s["last_watermark"] = watermark
    rows = []
    for s in stats.values():
        for key in ("avg_input_rows_per_s", "avg_batch_ms"):
            values = s[key]
            s[key] = round(sum(values) / len(values), 1) if values else 0.0
        s["max_processed_rows_per_s"] = round(
            s["max_processed_rows_per_s"], 1)
        rows.append(s)
    return rows


def window_reconciliation(matched, windows):
    """Compare the streamed windows with a batch recount of the raw sink.

    The batch recount uses every matched event, including the ones Spark
    dropped because they were behind the watermark and the ones of the
    windows that were still open when the job stopped.
    """
    batch = (
        matched.groupBy(F.window("event_time", C.WINDOW))
        .agg(F.count("*").alias("batch_edits"),
             F.countDistinct("imdb_id").alias("batch_entities"))
        .select(F.col("window.start").alias("window_start"),
                F.col("window.end").alias("window_end"),
                "batch_edits", "batch_entities")
    )
    streamed = windows.groupBy("window_start", "window_end").agg(
        F.sum("edits").alias("streamed_edits"))
    return (
        batch.join(streamed, ["window_start", "window_end"], "full")
        .withColumn("emitted_by_stream", F.col("streamed_edits").isNotNull())
        .withColumn("missing_in_stream",
                    F.col("batch_edits")
                    - F.coalesce("streamed_edits", F.lit(0)))
        .orderBy("window_start")
    )


def main():
    spark = get_spark("streaming-summary")
    matched = spark.read.parquet(C.MATCHED_EVENTS)
    windows = spark.read.parquet(C.ENTITY_WINDOWS)
    traffic = spark.read.parquet(C.TRAFFIC_WINDOWS)

    write_output(matched.agg(
        F.min("event_time").alias("first_event"),
        F.max("event_time").alias("last_event"),
        F.count("*").alias("matched_events"),
        F.countDistinct("imdb_id").alias("distinct_imdb_entities"),
        F.sum(F.col("delayed_beyond_watermark").cast("int"))
        .alias("delayed_beyond_watermark"),
        F.round(F.avg("ingestion_delay_s"), 1).alias("avg_delay_s"),
        F.max("ingestion_delay_s").alias("max_delay_s"),
    ), C.SECTION, "overview")

    write_output(
        matched.groupBy("entity_type", "match_type", "bare_key").count()
        .orderBy(F.desc("count")),
        C.SECTION, "matches_by_type")

    write_output(
        matched.groupBy("imdb_id", "imdb_name", "entity_type")
        .agg(F.count("*").alias("edits"),
             F.countDistinct("user").alias("editors"),
             F.sum("bytes_delta").alias("bytes_delta"))
        .orderBy(F.desc("edits"), "imdb_id"),
        C.SECTION, "top_entities", preview_rows=20)

    write_output(
        windows.groupBy("window_start", "window_end")
        .agg(F.sum("edits").alias("matched_edits"),
             F.count("*").alias("entities"))
        .join(traffic, ["window_start", "window_end"], "right")
        .withColumn("matched_edits",
                    F.coalesce("matched_edits", F.lit(0)))
        .withColumn("match_rate_pct", F.round(
            100 * F.col("matched_edits") / F.col("article_edits"), 2))
        .orderBy("window_start"),
        C.SECTION, "finalised_windows")

    write_output(window_reconciliation(matched, windows), C.SECTION,
                 "window_reconciliation", preview_rows=40)

    write_output(
        matched.where("delayed_beyond_watermark")
        .select("event_time", "kafka_time", "ingestion_delay_s", "title",
                "imdb_id", "match_type")
        .orderBy("event_time"),
        C.SECTION, "late_events", preview_rows=20)

    write_output(
        matched.select("event_time", "title", "imdb_id", "entity_type",
                       "match_type", "user", "bytes_delta",
                       "delayed_beyond_watermark")
        .orderBy("event_time"),
        C.SECTION, "matched_events", preview_rows=30)

    metrics = progress_metrics(C.METRICS_FILE)
    if metrics:
        df = spark.createDataFrame(metrics).select(
            "query", "batches", "input_rows", "avg_input_rows_per_s",
            "max_processed_rows_per_s", "avg_batch_ms", "max_batch_ms",
            "rows_dropped_by_watermark", "last_watermark")
        write_output(df, C.SECTION, "query_metrics")
        df.show(truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
