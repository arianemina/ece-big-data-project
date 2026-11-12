"""Summarise the outputs and metrics of a streaming run (Spark batch).

Prints Markdown tables (to paste in REPORT.md) and writes them to
``data/streaming/output/summary.md``.

Usage:
    python -m src.streaming.summarize
"""
import json
import os

from pyspark.sql import functions as F

from src.common.spark import get_spark
from src.streaming import config as C


def to_markdown(df, limit=20):
    rows = df.limit(limit).collect()
    cols = df.columns
    lines = ["| " + " | ".join(cols) + " |",
             "| " + " | ".join("---" for _ in cols) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(
            "" if row[c] is None else str(row[c]).replace("|", "\\|")
            for c in cols) + " |")
    return "\n".join(lines)


def progress_metrics(path):
    """Aggregate the StreamingQueryProgress reports per query."""
    stats = {}
    if not os.path.exists(path):
        return stats
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            p = json.loads(line)
            s = stats.setdefault(p["name"], {
                "batches": 0, "input_rows": 0, "max_input_rows_per_s": 0.0,
                "max_processed_rows_per_s": 0.0, "max_batch_ms": 0,
                "rows_dropped_by_watermark": 0, "last_watermark": None,
            })
            s["batches"] += 1
            s["input_rows"] += p.get("numInputRows", 0)
            s["max_input_rows_per_s"] = max(
                s["max_input_rows_per_s"], p.get("inputRowsPerSecond") or 0)
            s["max_processed_rows_per_s"] = max(
                s["max_processed_rows_per_s"],
                p.get("processedRowsPerSecond") or 0)
            s["max_batch_ms"] = max(
                s["max_batch_ms"],
                p.get("durationMs", {}).get("triggerExecution", 0))
            for op in p.get("stateOperators", []):
                s["rows_dropped_by_watermark"] = max(
                    s["rows_dropped_by_watermark"],
                    op.get("numRowsDroppedByWatermark", 0))
            wm = p.get("eventTime", {}).get("watermark")
            if wm:
                s["last_watermark"] = wm
    return stats


def main():
    spark = get_spark("streaming-summary")
    sections = []

    matched = spark.read.parquet(C.MATCHED_EVENTS)
    windows = spark.read.parquet(C.ENTITY_WINDOWS)
    traffic = spark.read.parquet(C.TRAFFIC_WINDOWS)

    overview = matched.agg(
        F.min("event_time").alias("first_event"),
        F.max("event_time").alias("last_event"),
        F.count("*").alias("matched_events"),
        F.countDistinct("imdb_id").alias("distinct_imdb_entities"),
        F.sum(F.col("is_late").cast("int")).alias("late_events"),
        F.round(F.avg("ingestion_delay_s"), 1).alias("avg_delay_s"),
        F.max("ingestion_delay_s").alias("max_delay_s"),
    )
    sections.append(("Overview of matched events", overview))
    sections.append(("Matches by entity and match type",
                     matched.groupBy("entity_type", "match_type").count()
                     .orderBy(F.desc("count"))))
    sections.append(("Most edited IMDb entities",
                     matched.groupBy("imdb_id", "imdb_name", "entity_type")
                     .agg(F.count("*").alias("edits"),
                          F.countDistinct("user").alias("editors"),
                          F.sum("bytes_delta").alias("bytes_delta"))
                     .orderBy(F.desc("edits"))))
    per_window = (
        windows.groupBy("window_start", "window_end")
        .agg(F.sum("edits").alias("matched_edits"))
        .join(traffic, ["window_start", "window_end"], "right")
        .withColumn("match_rate_pct", F.round(
            100 * F.coalesce("matched_edits", F.lit(0))
            / F.col("article_edits"), 2))
        .orderBy("window_start")
    )
    sections.append(("Finalised 5-minute windows (event time)",
                     per_window))
    sections.append(("Sample of matched events",
                     matched.select("event_time", "title", "imdb_id",
                                    "match_type", "user", "bytes_delta",
                                    "is_late")
                     .orderBy("event_time")))

    out = []
    for title, df in sections:
        out.append(f"### {title}\n\n{to_markdown(df)}\n")
    metrics = progress_metrics(C.METRICS_FILE)
    if metrics:
        keys = list(next(iter(metrics.values())))
        lines = ["| query | " + " | ".join(keys) + " |",
                 "| --- | " + " | ".join("---" for _ in keys) + " |"]
        for name, s in metrics.items():
            lines.append(f"| {name} | " + " | ".join(
                f"{s[k]:.1f}" if isinstance(s[k], float) else str(s[k])
                for k in keys) + " |")
        out.append("### Streaming query metrics\n\n" + "\n".join(lines)
                   + "\n")

    text = "\n".join(out)
    print(text)
    os.makedirs(C.OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(C.OUTPUT_DIR, "summary.md"), "w",
              encoding="utf-8") as fh:
        fh.write(text)
    spark.stop()


if __name__ == "__main__":
    main()
