"""Convert the raw IMDb TSV.gz files into Parquet with explicit schemas.

Usage (inside the spark container):
    python -m src.ingest_imdb                       # every downloaded table
    python -m src.ingest_imdb title.basics title.ratings
"""
import argparse
import os

from src.common.imdb import PARQUET_DIR, RAW_DIR, TABLES, read_raw
from src.common.spark import get_spark


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tables", nargs="*", default=None,
                        help="tables to convert (default: all downloaded)")
    args = parser.parse_args()

    tables = args.tables or [
        t for t in TABLES
        if os.path.exists(os.path.join(RAW_DIR, f"{t}.tsv.gz"))
    ]
    spark = get_spark("imdb-ingest")
    for table in tables:
        print(f"Converting {table} ...")
        out = os.path.join(PARQUET_DIR, table)
        read_raw(spark, table).write.mode("overwrite").parquet(out)
        count = spark.read.parquet(out).count()
        print(f"  {table}: {count:,} rows -> {out}")
    spark.stop()


if __name__ == "__main__":
    main()
