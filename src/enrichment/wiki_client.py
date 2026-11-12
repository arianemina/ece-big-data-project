"""Polite HTTP client for the Wikimedia APIs.

Implements the Wikimedia API etiquette:
- a descriptive User-Agent (``WIKI_USER_AGENT`` environment variable),
- requests sent one at a time with a minimum delay between them,
- ``maxlag`` on MediaWiki API calls (the client backs off when the servers
  are lagging),
- ``Retry-After`` honoured on HTTP 429/503, exponential back-off otherwise.
"""
import os
import time

import requests

DEFAULT_USER_AGENT = (
    "ECEBigDataStudentProject/1.0 (educational use; python-requests)"
)


class RateLimitedClient:
    """Sequential HTTP client enforcing a minimum interval between calls."""

    def __init__(self, min_interval, max_retries=6, timeout=60):
        self.min_interval = min_interval
        self.max_retries = max_retries
        self.timeout = timeout
        self._last_call = 0.0
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": os.environ.get("WIKI_USER_AGENT",
                                         DEFAULT_USER_AGENT),
            "Accept-Encoding": "gzip",
        })

    def _wait_turn(self):
        elapsed = time.monotonic() - self._last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last_call = time.monotonic()

    def request(self, method, url, **kwargs):
        """Send a request, retrying on throttling and transient errors.

        Returns the decoded JSON body.
        """
        delay = 2.0
        for attempt in range(1, self.max_retries + 1):
            self._wait_turn()
            try:
                resp = self.session.request(method, url,
                                            timeout=self.timeout, **kwargs)
            except requests.RequestException as exc:
                if attempt == self.max_retries:
                    raise
                print(f"  network error ({exc}); retry in {delay:.0f}s")
                time.sleep(delay)
                delay *= 2
                continue

            if resp.status_code in (429, 503) or resp.status_code >= 500:
                wait = float(resp.headers.get("Retry-After", delay))
                if attempt == self.max_retries:
                    resp.raise_for_status()
                print(f"  HTTP {resp.status_code}; retry in {wait:.0f}s")
                time.sleep(wait)
                delay *= 2
                continue
            resp.raise_for_status()
            body = resp.json()

            # MediaWiki reports replication lag as an API error.
            error = body.get("error", {}) if isinstance(body, dict) else {}
            if error.get("code") == "maxlag":
                wait = float(resp.headers.get("Retry-After", 5))
                print(f"  servers lagging; retry in {wait:.0f}s")
                time.sleep(wait)
                continue
            return body
        raise RuntimeError(f"giving up on {url}")
