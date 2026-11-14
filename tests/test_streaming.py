"""Tests for the streaming logic on static DataFrames (no Kafka needed)."""

from pyspark.sql import functions as F

from imdb.streaming import build_reference, stream_processor

BASICS = ("tconst STRING, titleType STRING, primaryTitle STRING, "
          "startYear INT")


def test_title_and_person_keys(spark):
    basics = spark.createDataFrame(
        [("tt1", "movie", "Inception", 2010),
         ("tt4", "movie", "The Matrix", 1999),
         ("tt2", "tvSeries", "Dark", 2017),
         ("tt3", "movie", "Unknown", 2001)], BASICS)
    ratings = spark.createDataFrame(
        [("tt1", 2500000), ("tt2", 500000), ("tt3", 10), ("tt4", 2200000)],
        "tconst STRING, numVotes INT")
    keys, titles = build_reference.title_keys(basics, ratings, 5000)
    got = {r.match_key for r in keys.collect()}
    assert {"inception (film)", "inception (2010 film)",
            "dark (tv series)", "dark (2017 tv series)"} <= got
    # one-word titles are only matched with a disambiguation suffix
    assert "inception" not in got and "dark" not in got
    assert "the matrix" in got                  # two words: bare title kept
    assert not any(k.startswith("unknown") for k in got)  # too few votes

    principals = spark.createDataFrame(
        [("tt1", "nm1", "director"), ("tt1", "nm2", "actress")],
        "tconst STRING, nconst STRING, category STRING")
    names = spark.createDataFrame(
        [("nm1", "Christopher Nolan"), ("nm2", "Elliot Page")],
        "nconst STRING, primaryName STRING")
    people = {r.match_key for r in build_reference.person_keys(
        principals, names, titles).collect()}
    assert "christopher nolan (director)" in people
    assert "christopher nolan (filmmaker)" in people
    assert "elliot page (actress)" in people
    assert "christopher nolan (actor)" not in people   # job not held


def test_filter_and_match(spark):
    events = spark.createDataFrame(
        [("enwiki", 0, "edit", "Inception", 1794500000, 1794500030),
         ("enwiki", 1, "edit", "Talk:Inception", 1794500000, 1794500030),
         ("frwiki", 0, "edit", "Inception", 1794500000, 1794500030),
         ("enwiki", 0, "edit", "Inception", 1794499000, 1794500030),
         ("enwiki", 0, "log", "Inception", 1794500000, 1794500030)],
        "wiki STRING, namespace INT, type STRING, title STRING, "
        "timestamp LONG, kafka_ts LONG",
    ).select(
        "*",
        F.timestamp_seconds("timestamp").alias("event_time"),
        F.timestamp_seconds("kafka_ts").alias("kafka_time"),
        F.lit(None).cast("string").alias("user"),
        F.lit(False).alias("bot"), F.lit(False).alias("minor"),
        F.lit(None).cast("string").alias("comment"),
        F.struct(F.lit(10).cast("long").alias("old"),
                 F.lit(25).cast("long").alias("new")).alias("length"),
        F.struct(F.lit(1).cast("long").alias("old"),
                 F.lit(2).cast("long").alias("new")).alias("revision"),
        F.struct(F.lit("u").alias("uri")).alias("meta"),
    )
    reference = spark.createDataFrame(
        [("inception", "film", "tt1", "Inception", 1, "imdb_title", True,
          1)],
        "match_key STRING, entity_type STRING, imdb_id STRING, "
        "imdb_name STRING, popularity LONG, match_type STRING, "
        "bare_key BOOLEAN, n_candidates LONG")
    articles = stream_processor.filter_articles(events, ["enwiki"])
    assert articles.count() == 2              # namespace, wiki, type filters
    matched = stream_processor.match_imdb(articles, reference, 600) \
        .orderBy("event_time").collect()
    assert [m.imdb_id for m in matched] == ["tt1", "tt1"]
    # ingestion delays of 1030 s and 30 s against a 600 s watermark
    assert [m.delayed_beyond_watermark for m in matched] == [True, False]
    assert matched[1].bytes_delta == 15


def test_window_reconciliation_counts_events_missing_in_stream(spark):
    from imdb.streaming import summarize
    matched = spark.createDataFrame(
        [("2026-11-12 10:01:00", "tt1"), ("2026-11-12 10:02:00", "tt2"),
         ("2026-11-12 10:07:00", "tt1")],
        "event_time STRING, imdb_id STRING",
    ).withColumn("event_time", F.to_timestamp("event_time"))
    windows = spark.createDataFrame(
        [("2026-11-12 10:00:00", "2026-11-12 10:05:00", 1)],
        "window_start STRING, window_end STRING, edits LONG",
    ).select(F.to_timestamp("window_start").alias("window_start"),
             F.to_timestamp("window_end").alias("window_end"), "edits")
    rows = summarize.window_reconciliation(matched, windows).collect()
    assert [(r.batch_edits, r.streamed_edits, r.missing_in_stream,
             r.emitted_by_stream) for r in rows] == [
        (2, 1, 1, True), (1, None, 1, False)]


def test_to_seconds():
    assert stream_processor.to_seconds("10 minutes") == 600
    assert stream_processor.to_seconds("30 seconds") == 30
