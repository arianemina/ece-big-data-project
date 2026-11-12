"""Spark Structured Streaming job: Wikipedia changes relevant to IMDb.

Pipeline:
    Kafka topic ``wikipedia.recentchange``
      -> parse JSON with an explicit schema
      -> keep article edits/creations on English Wikipedia
      -> event time = time of the edit on Wikipedia (``timestamp`` field)
      -> stream-static join with the IMDb reference table on the page title
      -> three sinks (Parquet):
         * ``matched_events``  every matching edit (stateless, append), with
           its ingestion delay and an ``is_late`` flag,
         * ``entity_windows``  edits per IMDb entity per 5-minute event-time
           window, finalised once the 10-minute watermark has passed,
         * ``traffic_windows`` all filtered edits per window (denominator
           used to compute the match rate).

Late data: windows are aggregated on event time with a watermark of
``WATERMARK``; events later than that are excluded from the aggregates by
Spark (counted in the ``numRowsDroppedByWatermark`` metric) but are still
kept in ``matched_events`` with ``is_late = true`` so that they can be
reconciled in batch afterwards.

Every micro-batch progress report is appended to
``data/streaming/metrics/progress.jsonl``.

Usage:
    python -m imdb.streaming.stream_processor [--duration-minutes 20]
"""
import argparse
import json
import os

from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.streaming import StreamingQueryListener

from imdb.streaming import config as C
from imdb.streaming.session import get_streaming_spark

EVENT_SCHEMA = T.StructType([
    T.StructField("id", T.LongType()),
    T.StructField("type", T.StringType()),
    T.StructField("namespace", T.IntegerType()),
    T.StructField("title", T.StringType()),
    T.StructField("title_url", T.StringType()),
    T.StructField("comment", T.StringType()),
    T.StructField("timestamp", T.LongType()),
    T.StructField("user", T.StringType()),
    T.StructField("bot", T.BooleanType()),
    T.StructField("minor", T.BooleanType()),
    T.StructField("wiki", T.StringType()),
    T.StructField("server_name", T.StringType()),
    T.StructField("length", T.StructType([
        T.StructField("old", T.LongType()),
        T.StructField("new", T.LongType()),
    ])),
    T.StructField("revision", T.StructType([
        T.StructField("old", T.LongType()),
        T.StructField("new", T.LongType()),
    ])),
    T.StructField("meta", T.StructType([
        T.StructField("id", T.StringType()),
        T.StructField("dt", T.StringType()),
        T.StructField("uri", T.StringType()),
    ])),
])


class ProgressLogger(StreamingQueryListener):
    """Append every query progress report to a JSON Lines file.

    It also prints one line per micro-batch, which serves as the live view
    of the job (a separate console sink would duplicate the join).
    """

    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def onQueryStarted(self, event):
        print(f"query started: {event.name}")

    def onQueryProgress(self, event):
        progress = json.loads(event.progress.json)
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(progress) + "\n")
        print(
            f"[{progress['name']}] batch {progress['batchId']}: "
            f"{progress['numInputRows']} rows, "
            f"{progress.get('processedRowsPerSecond', 0):.1f} rows/s, "
            f"watermark {progress.get('eventTime', {}).get('watermark')}"
        )

    def onQueryIdle(self, event):
        pass

    def onQueryTerminated(self, event):
        print(f"query terminated: {event.id}")


def to_seconds(interval):
    """'10 minutes' -> 600, '30 seconds' -> 30."""
    value, unit = interval.split()
    factor = {"second": 1, "minute": 60, "hour": 3600}[unit.rstrip("s")]
    return int(value) * factor


def read_events(spark, bootstrap, topic, starting_offsets):
    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", bootstrap)
        .option("subscribe", topic)
        .option("startingOffsets", starting_offsets)
        .option("failOnDataLoss", "false")
        .option("maxOffsetsPerTrigger", 20000)
        .load()
    )
    return (
        raw.select(
            F.from_json(F.col("value").cast("string"), EVENT_SCHEMA)
             .alias("e"),
            F.col("timestamp").alias("kafka_time"),
        )
        .select("e.*", "kafka_time")
        .withColumn("event_time", F.timestamp_seconds("timestamp"))
    )


def filter_articles(events, wikis):
    """Main-namespace edits and page creations on the selected wikis."""
    return events.filter(
        F.col("wiki").isin(wikis)
        & (F.col("namespace") == 0)
        & F.col("type").isin("edit", "new")
        & F.col("event_time").isNotNull()
    )


def match_imdb(articles, reference, watermark_seconds):
    lateness = (F.unix_timestamp("kafka_time")
                - F.unix_timestamp("event_time"))
    return (
        articles.withColumn("match_key", F.lower(F.trim("title")))
        .join(F.broadcast(reference), "match_key", "inner")
        .select(
            "event_time", "kafka_time", "wiki", "title", "type", "user",
            "bot", "minor", "comment",
            (F.col("length.new") - F.coalesce(F.col("length.old"),
                                              F.lit(0)))
            .alias("bytes_delta"),
            F.col("revision.new").alias("revision_id"),
            F.col("meta.uri").alias("event_uri"),
            "imdb_id", "imdb_name", "entity_type", "match_type",
            "n_candidates",
            lateness.alias("ingestion_delay_s"),
            (lateness > watermark_seconds).alias("is_late"),
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration-minutes", type=float, default=20)
    parser.add_argument("--bootstrap", default=C.KAFKA_BOOTSTRAP)
    parser.add_argument("--topic", default=C.TOPIC)
    parser.add_argument("--starting-offsets", default="latest",
                        choices=["latest", "earliest"])
    parser.add_argument("--wikis", nargs="+", default=C.WIKIS)
    parser.add_argument("--window", default=C.WINDOW)
    parser.add_argument("--watermark", default=C.WATERMARK)
    parser.add_argument("--trigger", default=C.TRIGGER)
    args = parser.parse_args()

    spark = get_streaming_spark("wikipedia-imdb-stream")
    spark.streams.addListener(ProgressLogger(C.METRICS_FILE))

    watermark_seconds = to_seconds(args.watermark)
    reference = spark.read.parquet(C.REFERENCE).cache()
    print(f"reference keys loaded: {reference.count():,}")

    events = read_events(spark, args.bootstrap, args.topic,
                         args.starting_offsets)
    articles = filter_articles(events, args.wikis)
    matched = match_imdb(articles, reference, watermark_seconds)

    def sink(df, name, mode="append"):
        return (
            df.writeStream.queryName(name).outputMode(mode)
            .format("parquet")
            .option("path", os.path.join(C.SINK_DIR, name))
            .option("checkpointLocation",
                    os.path.join(C.CHECKPOINT_DIR, name))
            .trigger(processingTime=args.trigger)
            .start()
        )

    # 1. every matching event (stateless; late events are kept and flagged)
    sink(matched, "matched_events")

    # 2. edits per IMDb entity per event-time window (finalised windows)
    entity_windows = (
        matched.withWatermark("event_time", args.watermark)
        .groupBy(F.window("event_time", args.window), "imdb_id",
                 "imdb_name", "entity_type")
        .agg(
            F.count("*").alias("edits"),
            F.sum(F.col("bot").cast("int")).alias("bot_edits"),
            F.approx_count_distinct("user").alias("distinct_editors"),
            F.sum("bytes_delta").alias("bytes_delta"),
            F.collect_set("title").alias("titles"),
        )
        .select(F.col("window.start").alias("window_start"),
                F.col("window.end").alias("window_end"), "*")
        .drop("window")
    )
    sink(entity_windows, "entity_windows")

    # 3. all English Wikipedia article edits per window (match rate)
    traffic = (
        articles.withWatermark("event_time", args.watermark)
        .groupBy(F.window("event_time", args.window))
        .agg(F.count("*").alias("article_edits"),
             F.sum(F.col("bot").cast("int")).alias("bot_edits"))
        .select(F.col("window.start").alias("window_start"),
                F.col("window.end").alias("window_end"),
                "article_edits", "bot_edits")
    )
    sink(traffic, "traffic_windows")

    timeout = args.duration_minutes * 60 if args.duration_minutes else None
    spark.streams.awaitAnyTermination(timeout)
    for query in spark.streams.active:
        query.stop()
    print("Streaming stopped.")
    spark.stop()


if __name__ == "__main__":
    main()
