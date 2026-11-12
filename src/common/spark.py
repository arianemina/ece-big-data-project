"""Shared SparkSession factory."""
import os

from pyspark.sql import SparkSession

SPARK_VERSION = "4.2.0"
SCALA_VERSION = "2.13"
KAFKA_PACKAGE = (
    f"org.apache.spark:spark-sql-kafka-0-10_{SCALA_VERSION}:{SPARK_VERSION}"
)


def get_spark(app_name, with_kafka=False, shuffle_partitions=8):
    """Return a local SparkSession tuned for a laptop-sized container.

    Args:
        app_name: name shown in the Spark UI.
        with_kafka: also load the Kafka connector (needed for streaming).
        shuffle_partitions: default number of shuffle partitions.
    """
    builder = (
        SparkSession.builder.appName(app_name)
        .master(os.environ.get("SPARK_MASTER", "local[*]"))
        .config("spark.driver.memory",
                os.environ.get("SPARK_DRIVER_MEMORY", "2g"))
        .config("spark.sql.shuffle.partitions", str(shuffle_partitions))
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.ui.showConsoleProgress", "false")
    )
    if with_kafka:
        builder = builder.config("spark.jars.packages", KAFKA_PACKAGE)
    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark
