"""Forward Wikimedia EventStreams ``recentchange`` events to Kafka.

The Wikimedia EventStreams service publishes every edit made on Wikimedia
projects as Server-Sent Events (SSE). This producer reads the SSE stream and
publishes each event, unchanged, as a JSON message in the Kafka topic
``wikipedia.recentchange`` (key = ``<wiki>:<page title>``).

- Reconnects automatically and resumes from the last event ID received.
- ``--since-minutes N`` replays events from N minutes ago (EventStreams
  history); it is used to inject late-arriving data into a running stream.

Usage:
    python -m src.streaming.producer [--duration-minutes 30]
                                     [--since-minutes N] [--max-events N]
"""
import argparse
import json
import os
import time
from datetime import datetime, timedelta, timezone

import requests
from kafka import KafkaProducer

from src.streaming import config as C

USER_AGENT = os.environ.get(
    "WIKI_USER_AGENT",
    "ECEBigDataStudentProject/1.0 (educational use; python-requests)",
)


class Done(Exception):
    """Raised when the duration or event limit is reached."""


def sse_events(url, params, last_event_id=None):
    """Yield (event_id, data) tuples from a Server-Sent Events stream."""
    headers = {"Accept": "text/event-stream", "User-Agent": USER_AGENT}
    if last_event_id:
        headers["Last-Event-ID"] = last_event_id
    with requests.get(url, params=params, headers=headers, stream=True,
                      timeout=(10, 60)) as resp:
        resp.raise_for_status()
        event_id, data = None, []
        for raw in resp.iter_lines(decode_unicode=True):
            if raw is None:
                continue
            if raw == "":                       # end of one event
                if data:
                    yield event_id, "\n".join(data)
                event_id, data = None, []
            elif raw.startswith("id:"):
                event_id = raw[3:].strip()
            elif raw.startswith("data:"):
                data.append(raw[5:].lstrip())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration-minutes", type=float, default=0,
                        help="stop after this many minutes (0 = never)")
    parser.add_argument("--since-minutes", type=float, default=0,
                        help="replay events starting N minutes in the past")
    parser.add_argument("--max-events", type=int, default=0)
    parser.add_argument("--bootstrap", default=C.KAFKA_BOOTSTRAP)
    parser.add_argument("--topic", default=C.TOPIC)
    args = parser.parse_args()

    producer = KafkaProducer(
        bootstrap_servers=args.bootstrap,
        linger_ms=50, acks=1,
    )
    params = {}
    if args.since_minutes:
        since = datetime.now(timezone.utc) - timedelta(
            minutes=args.since_minutes)
        params["since"] = since.strftime("%Y-%m-%dT%H:%M:%SZ")

    deadline = (time.time() + args.duration_minutes * 60
                if args.duration_minutes else None)
    sent, last_id, backoff = 0, None, 1
    print(f"Producing to {args.topic} on {args.bootstrap} ...")
    while True:
        try:
            for event_id, data in sse_events(C.EVENTSTREAMS_URL, params,
                                             last_id):
                last_id = event_id or last_id
                try:
                    event = json.loads(data)
                except ValueError:
                    continue
                if event.get("meta", {}).get("domain") == "canary":
                    continue                    # monitoring events
                key = f"{event.get('wiki')}:{event.get('title')}"
                producer.send(args.topic, key=key.encode("utf-8"),
                              value=data.encode("utf-8"))
                sent += 1
                backoff = 1
                if sent % 1000 == 0:
                    print(f"  {sent:,} events sent")
                if (args.max_events and sent >= args.max_events) or (
                        deadline and time.time() > deadline):
                    raise Done
            # The server closed the stream: reconnect from last_id.
        except Done:
            break
        except (requests.RequestException, ValueError) as exc:
            print(f"  stream interrupted ({exc}); reconnecting in "
                  f"{backoff}s")
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)
        if last_id:
            params.pop("since", None)   # resume with Last-Event-ID instead
    producer.flush()
    print(f"Done: {sent:,} events sent to Kafka")


if __name__ == "__main__":
    main()
