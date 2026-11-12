# Spark 4.2.0 / Python 3.13 / OpenJDK 21 (image pinned by digest for reproducibility)
FROM quay.io/jupyter/pyspark-notebook@sha256:7e102d041c42cca6e0d32269cded10fad2c377aeb09fad1ec546840660d691c4

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /home/jovyan/work

# Make pyspark importable from any shell (not only from the notebook start hooks)
ENV PYTHONPATH=/usr/local/spark/python:/usr/local/spark/python/lib/py4j-0.10.9.9-src.zip \
    PYSPARK_PYTHONPATH_SET=1 \
    PYTHONUNBUFFERED=1
