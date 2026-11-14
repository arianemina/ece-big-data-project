# Python + Java runtime for the Spark jobs (same pinned versions as a local
# virtualenv: see requirements.txt).
FROM python:3.12-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless procps curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1

WORKDIR /app
CMD ["sleep", "infinity"]
