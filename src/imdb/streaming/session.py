"""Spark session with the Kafka connector for Structured Streaming."""

import os

import pyspark
from pyspark.sql import SparkSession

# The connector version must match the installed Spark version.
KAFKA_PACKAGE = (
    f"org.apache.spark:spark-sql-kafka-0-10_2.13:{pyspark.__version__}"
)


def get_streaming_spark(app_name):
    builder = (
        SparkSession.builder
        .appName(app_name)
        .master(os.environ.get("SPARK_MASTER", "local[*]"))
        .config("spark.driver.memory",
                os.environ.get("SPARK_DRIVER_MEMORY", "4g"))
        # Small micro-batches: a few shuffle partitions are enough.
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.ui.showConsoleProgress", "false")
        .config("spark.jars.packages", KAFKA_PACKAGE)
    )
    if os.environ.get("SPARK_IVY_DIR"):
        builder = builder.config("spark.jars.ivy",
                                 os.environ["SPARK_IVY_DIR"])
    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark
