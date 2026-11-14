"""Country of birth of the enriched principals, from Wikidata (no Spark).

For every person whose Wikidata item was found by the enrichment step, the
place of birth (P19) and the country of that place (P17, with its ISO 3166
code P297) are queried with SPARQL, 200 items per query, one query per
second. Answers are appended to a JSON Lines file with their source and
retrieval time; the script is resumable (items already present are
skipped). Wikidata content is CC0.

Usage: python -m imdb.open_question.fetch_birth_countries
"""

import json
import os
from datetime import datetime, timezone

from imdb.enrichment import config as E
from imdb.enrichment.fetch_wikipedia import (already_done, append, batches,
                                             now_iso)
from imdb.enrichment.wiki_client import RateLimitedClient
from imdb.open_question import config as C

BATCH = 200
INTERVAL = 1.0     # seconds between SPARQL queries

QUERY = """
SELECT ?item ?place ?country ?iso ?countryLabel WHERE {
  VALUES ?item { %s }
  ?item wdt:P19 ?place .
  OPTIONAL {
    ?place wdt:P17 ?country .
    OPTIONAL { ?country wdt:P297 ?iso . }
    OPTIONAL { ?country rdfs:label ?countryLabel .
               FILTER (lang(?countryLabel) = "en") }
  }
}
"""


def person_items(links_path):
    """Wikidata item ids (Q...) of the people found by the enrichment."""
    items = set()
    with open(links_path, encoding="utf-8") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if rec.get("entity_type") == "person" and rec.get("wikidata_uri"):
                items.add(rec["wikidata_uri"].rsplit("/", 1)[1])
    return sorted(items)


def to_records(batch, bindings, retrieved_at):
    """One record per (item, country); items without P19 get one empty row."""
    records, seen = [], set()
    for row in bindings:
        item = row["item"]["value"].rsplit("/", 1)[1]
        seen.add(item)
        records.append({
            "wikidata_id": item,
            "birth_place_uri": row["place"]["value"],
            "country_uri": row.get("country", {}).get("value"),
            "country_iso": row.get("iso", {}).get("value"),
            "country_label": row.get("countryLabel", {}).get("value"),
            "source_uri": E.WIKIDATA_SPARQL,
            "retrieved_at": retrieved_at,
        })
    for item in batch:
        if item not in seen:
            records.append({
                "wikidata_id": item, "birth_place_uri": None,
                "country_uri": None, "country_iso": None,
                "country_label": None, "source_uri": E.WIKIDATA_SPARQL,
                "retrieved_at": retrieved_at,
            })
    return records


def main():
    client = RateLimitedClient(INTERVAL)
    items = person_items(E.RAW_LINKS)
    done = already_done(C.RAW_COUNTRIES, key="wikidata_id")
    todo = [i for i in items if i not in done]
    print(f"{len(todo):,} of {len(items):,} Wikidata items to query")
    os.makedirs(os.path.dirname(C.RAW_COUNTRIES), exist_ok=True)
    for n, batch in enumerate(batches(todo, BATCH), 1):
        values = " ".join(f"wd:{i}" for i in batch)
        body = client.request(
            "POST", E.WIKIDATA_SPARQL,
            data={"query": QUERY % values, "format": "json"},
            headers={"Accept": "application/sparql-results+json"})
        append(C.RAW_COUNTRIES,
               to_records(batch, body["results"]["bindings"], now_iso()))
        if n % 10 == 0:
            print(f"  {n * BATCH:,} items done")
    print(f"done at {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
