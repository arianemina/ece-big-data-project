"""Gather raw enrichment data from Wikidata and English Wikipedia.

Data gathering is done outside Spark (allowed by the instructions); the raw
API answers are appended to JSON Lines files and every later step (cleaning,
section extraction, schema enforcement, joins) is done in Spark by
``src.enrichment.build_enriched``.

Steps:
1. ``links``  - map IMDb IDs to Wikidata items and English Wikipedia
   articles with SPARQL (Wikidata property P345 = IMDb ID). For people the
   birth date, death date and place of birth are fetched at the same time.
2. ``films``  - download the plain-text article of every film (the plot
   section is extracted later in Spark).
3. ``people`` - download the lead section (biography) of every principal,
   20 articles per request.

Each step is resumable: IDs already present in the output file are skipped,
so an interrupted run can simply be restarted.

Usage:
    python -m src.enrichment.fetch_wikipedia [--steps links films people]
                                            [--limit N]
"""
import argparse
import json
import os
from datetime import datetime, timezone
from urllib.parse import quote, unquote

import pyarrow.parquet as pq

from src.enrichment import config as C
from src.enrichment.wiki_client import RateLimitedClient

SPARQL_BATCH = 200
PEOPLE_BATCH = 20          # MediaWiki limit for intro extracts per request
WIKIDATA_INTERVAL = 1.0    # seconds between SPARQL queries
WIKIPEDIA_INTERVAL = 0.2   # seconds between MediaWiki API calls (5 req/s)

FILM_QUERY = """
SELECT ?imdb ?item ?article WHERE {
  VALUES ?imdb { %s }
  ?item wdt:P345 ?imdb .
  OPTIONAL { ?article schema:about ?item ;
                      schema:isPartOf <https://en.wikipedia.org/> . }
}
"""

PERSON_QUERY = """
SELECT ?imdb ?item ?article ?birth ?death ?birthPlaceLabel WHERE {
  VALUES ?imdb { %s }
  ?item wdt:P345 ?imdb .
  OPTIONAL { ?article schema:about ?item ;
                      schema:isPartOf <https://en.wikipedia.org/> . }
  OPTIONAL { ?item wdt:P569 ?birth . }
  OPTIONAL { ?item wdt:P570 ?death . }
  OPTIONAL { ?item wdt:P19 ?birthPlace .
             ?birthPlace rdfs:label ?birthPlaceLabel .
             FILTER (lang(?birthPlaceLabel) = "en") }
}
"""


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_ids(path):
    """Read the ``imdb_id`` column of a Parquet directory."""
    return sorted(set(pq.read_table(path, columns=["imdb_id"])
                      .column("imdb_id").to_pylist()))


def already_done(path, key="imdb_id"):
    """IDs already written to a JSON Lines output file."""
    done = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    done.add(json.loads(line)[key])
                except (ValueError, KeyError):
                    continue  # ignore a line truncated by an interruption
    return done


def append(path, records):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def batches(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def title_from_url(url):
    """'https://en.wikipedia.org/wiki/Blade_Runner' -> 'Blade Runner'."""
    return unquote(url.rsplit("/wiki/", 1)[1]).replace("_", " ")


# --------------------------------------------------------------------------
# Step 1: Wikidata links
# --------------------------------------------------------------------------
def fetch_links(client, ids, entity_type, out_path):
    todo = [i for i in ids if i not in already_done(out_path)]
    print(f"[links/{entity_type}] {len(todo):,} IDs to resolve")
    query = FILM_QUERY if entity_type == "film" else PERSON_QUERY
    for n, batch in enumerate(batches(todo, SPARQL_BATCH), 1):
        values = " ".join(f'"{i}"' for i in batch)
        body = client.request(
            "POST", C.WIKIDATA_SPARQL,
            data={"query": query % values, "format": "json"},
            headers={"Accept": "application/sparql-results+json"},
        )
        retrieved_at = now_iso()
        found = {}
        for row in body["results"]["bindings"]:
            imdb_id = row["imdb"]["value"]
            rec = found.setdefault(imdb_id, {
                "imdb_id": imdb_id,
                "entity_type": entity_type,
                "wikidata_uri": row["item"]["value"],
                "wikipedia_url": None,
                "birth_date": None,
                "death_date": None,
                "birth_place": None,
            })
            # Keep the first value of each optional field.
            if "article" in row and not rec["wikipedia_url"]:
                rec["wikipedia_url"] = row["article"]["value"]
            for field, var in (("birth_date", "birth"),
                               ("death_date", "death"),
                               ("birth_place", "birthPlaceLabel")):
                if var in row and not rec[field]:
                    rec[field] = row[var]["value"]
        records = []
        for imdb_id in batch:
            rec = found.get(imdb_id, {
                "imdb_id": imdb_id, "entity_type": entity_type,
                "wikidata_uri": None, "wikipedia_url": None,
                "birth_date": None, "death_date": None, "birth_place": None,
            })
            rec["source_uri"] = C.WIKIDATA_SPARQL
            rec["retrieved_at"] = retrieved_at
            records.append(rec)
        append(out_path, records)
        print(f"  batch {n}: {len(found)}/{len(batch)} found on Wikidata")


def load_links(path, entity_type):
    links = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec["entity_type"] == entity_type and rec["wikipedia_url"]:
                    links[rec["imdb_id"]] = title_from_url(
                        rec["wikipedia_url"])
    return links


# --------------------------------------------------------------------------
# Steps 2 and 3: Wikipedia pages
# --------------------------------------------------------------------------
def page_record(imdb_id, entity_type, requested_title, page, retrieved_at):
    rec = {
        "imdb_id": imdb_id,
        "entity_type": entity_type,
        "requested_title": requested_title,
        "page_id": None, "title": None, "revision_id": None,
        "page_url": None, "permalink": None, "extract": None,
        "status": "missing", "retrieved_at": retrieved_at,
    }
    if page and not page.get("missing") and not page.get("invalid"):
        revisions = page.get("revisions") or [{}]
        revid = revisions[0].get("revid")
        rec.update({
            "page_id": page.get("pageid"),
            "title": page.get("title"),
            "revision_id": revid,
            "page_url": page.get("fullurl"),
            "permalink": (
                f"https://en.wikipedia.org/w/index.php?title="
                f"{quote(page['title'].replace(' ', '_'))}&oldid={revid}"
                if revid else page.get("fullurl")
            ),
            "extract": page.get("extract"),
            "status": "ok",
        })
    return rec


def query_pages(client, titles, intro_only):
    params = {
        "action": "query", "format": "json", "formatversion": "2",
        "prop": "extracts|info|revisions", "inprop": "url",
        "rvprop": "ids", "explaintext": "1", "exsectionformat": "wiki",
        "redirects": "1", "maxlag": "5", "titles": "|".join(titles),
    }
    if intro_only:
        params.update({"exintro": "1", "exlimit": "max"})
    body = client.request("GET", C.WIKIPEDIA_API, params=params)
    query = body.get("query", {})
    # Follow normalisation and redirects back to the requested titles.
    mapping = {t: t for t in titles}
    for step in ("normalized", "redirects"):
        for item in query.get(step, []):
            for req, cur in mapping.items():
                if cur == item["from"]:
                    mapping[req] = item["to"]
    pages = {p["title"]: p for p in query.get("pages", [])}
    return {req: pages.get(cur) for req, cur in mapping.items()}


def fetch_pages(client, links, entity_type, out_path, batch_size, limit):
    done = already_done(out_path)
    todo = [(i, t) for i, t in sorted(links.items()) if i not in done]
    if limit:
        todo = todo[:limit]
    print(f"[{entity_type}] {len(todo):,} Wikipedia pages to fetch")
    intro_only = entity_type == "person"
    for n, batch in enumerate(batches(todo, batch_size), 1):
        pages = query_pages(client, [t for _, t in batch], intro_only)
        retrieved_at = now_iso()
        append(out_path, [
            page_record(i, entity_type, t, pages.get(t), retrieved_at)
            for i, t in batch
        ])
        if n % 50 == 0:
            print(f"  {n * batch_size:,} pages done")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", nargs="+",
                        default=["links", "films", "people"],
                        choices=["links", "films", "people"])
    parser.add_argument("--limit", type=int, default=0,
                        help="max number of pages per step (0 = all)")
    args = parser.parse_args()

    wikidata = RateLimitedClient(WIKIDATA_INTERVAL)
    wikipedia = RateLimitedClient(WIKIPEDIA_INTERVAL)

    film_ids = read_ids(C.TARGET_FILM_IDS)
    person_ids = read_ids(C.TARGET_PERSON_IDS)
    if args.limit:
        film_ids = film_ids[:args.limit]
        person_ids = person_ids[:args.limit]

    if "links" in args.steps:
        fetch_links(wikidata, film_ids, "film", C.RAW_LINKS)
        fetch_links(wikidata, person_ids, "person", C.RAW_LINKS)
    if "films" in args.steps:
        fetch_pages(wikipedia, load_links(C.RAW_LINKS, "film"), "film",
                    C.RAW_FILM_PAGES, 1, args.limit)
    if "people" in args.steps:
        fetch_pages(wikipedia, load_links(C.RAW_LINKS, "person"), "person",
                    C.RAW_PERSON_PAGES, PEOPLE_BATCH, args.limit)


if __name__ == "__main__":
    main()
