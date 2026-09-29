"""
Step 03: map each title to its Wikipedia article in each market's language.

Input:  data/processed/titles.csv, data/processed/title_markets.csv
Output: data/raw/wikidata_candidates.json    compact Wikidata answers per title (cache)
        data/processed/title_article_map.csv  (title_id, show_title, category, qid,
                                                match_method, market, lang, article)
        data/logs/wikidata_match_log.csv      one row per title: how the match went
        data/logs/dropped_pairs.csv           charted title-market pairs with no article

No translated titles are typed by hand. The English Netflix title is used
only to find the Wikidata item. The per-language article names come from
that item's sitelinks.

Finding candidates
  Search Wikidata for the English title (wbsearchentities, up to 200 hits).
  A hit is a candidate if its label, or the alias the search matched on,
  equals the Netflix title after ignoring case, curly vs straight quotes, and
  repeated whitespace.

Rule A: Netflix ID (preferred)
  Candidates that carry a Netflix ID (property P1874) are Netflix titles by
  Wikidata's own record, so they are accepted directly: no type check.
  Label and alias matches both count here, because the Netflix ID confirms
  identity. One such candidate is a match. Several are resolved with the
  date tie-break below.

Rule B: label, type, and date (only when no candidate has a Netflix ID)
  1. Keep candidates whose label (not alias) equals the title.
  2. Keep those whose type (P31, following subclass-of P279 upward) is on
     the allowlist for the Netflix category:
        Films -> film (Q11424) or television special (Q1261214)
        TV    -> television program (Q15416), which covers series,
                 miniseries, anime, reality shows, and so on.
  3. One survivor is a match. Several go to the date tie-break.

Date tie-break (used by both rules)
  Pick the candidate whose closest publication date (P577) or start time
  (P580) is nearest the end of the Netflix window. The title is dropped and
  logged when any candidate has no date (it could be the right one), when two
  are equally close, or when the winner is more than TIEBREAK_MAX_YEARS from
  the window. That last guard catches new releases that have no Wikidata item
  yet, where the "closest" candidate is an older namesake.

There is no date filter on a unique match, because long-running series can
start many years before the window.

Contested flag
  Wikidata keeps Netflix IDs on older titles that were once on Netflix. When
  a newer title with the same name charts (a remake, or a recent film with no
  Netflix ID on Wikidata yet), Rule A can pick the old one. Rule A matches
  are flagged `contested` when another candidate of an allowed type is newer
  than the chosen item. The match is kept; later steps decide how to use it.

Usage: python scripts/03_map_wikidata.py [--refresh]
  --refresh  ignore the cache and query Wikidata again for every title
"""

from __future__ import annotations

import argparse
import json
import re
import time
import unicodedata
from datetime import date

import pandas as pd

import config

# Type allowlist for Rule B, keyed by Netflix category.
TYPE_ROOTS = {
    "Films": {"Q11424": "film", "Q1261214": "television special"},
    "TV": {"Q15416": "television program"},
}

SEARCH_PAGE = 50   # wbsearchentities maximum page size
SEARCH_MAX = 200   # stop paging after this many hits

# In a tie-break, the winning candidate's nearest date must be within this
# many years of the window end, or the tie counts as unresolved.
TIEBREAK_MAX_YEARS = 2

LANG_WIKIS = [f"{lang}wiki" for lang in config.MARKETS.values()]


def normalize(label: str) -> str:
    """Case-fold and tidy a title so trivial formatting differences don't block a match."""
    s = unicodedata.normalize("NFKC", label)
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"\s+", " ", s).strip()
    return s.casefold()


# ---------------------------------------------------------------------------
# Wikidata queries. Each returns plain, JSON-serialisable data for the cache.
# ---------------------------------------------------------------------------

def search_candidates(title: str) -> dict[str, str]:
    """
    Return {qid: "label" | "alias"} for search hits whose label or matched
    alias equals the title. "label" wins if an item matches both ways.
    """
    target = normalize(title)
    found: dict[str, str] = {}
    offset = 0
    while offset < SEARCH_MAX:
        data = config.http_get(config.WIKIDATA_API, params={
            "action": "wbsearchentities", "search": title, "language": "en",
            "uselang": "en", "type": "item", "limit": SEARCH_PAGE,
            "continue": offset, "format": "json",
        }).json()
        for hit in data.get("search", []):
            if normalize(hit.get("label", "")) == target:
                found[hit["id"]] = "label"
            elif (hit.get("match", {}).get("type") == "alias"
                  and normalize(hit["match"].get("text", "")) == target):
                found.setdefault(hit["id"], "alias")
        if "search-continue" not in data:
            break
        offset = data["search-continue"]
        time.sleep(0.2)
    return found


def entity_dates(entity: dict) -> list[str]:
    """All P577 (publication date) and P580 (start time) values as ISO dates."""
    out: list[str] = []
    for prop in ("P577", "P580"):
        for claim in entity.get("claims", {}).get(prop, []):
            try:
                t = claim["mainsnak"]["datavalue"]["value"]["time"]  # "+2022-02-11T00:00:00Z"
            except KeyError:
                continue  # "unknown value" or "no value" statements
            m = re.match(r"^\+?(\d{4})-(\d{2})-(\d{2})", t)
            if m:
                y, mo, d = (int(x) for x in m.groups())
                out.append(date(y, max(mo, 1), max(d, 1)).isoformat())  # year-only -> Jan 1
    return out


def fetch_compact_entities(qids: list[str]) -> dict[str, dict]:
    """For each QID: Netflix IDs, dates, and the six sitelinks we care about."""
    out: dict[str, dict] = {}
    for i in range(0, len(qids), 50):
        ents = config.http_get(config.WIKIDATA_API, params={
            "action": "wbgetentities", "ids": "|".join(qids[i:i + 50]),
            "props": "claims|sitelinks", "format": "json",
        }).json()["entities"]
        for q, e in ents.items():
            netflix_ids = [c["mainsnak"]["datavalue"]["value"]
                           for c in e.get("claims", {}).get("P1874", [])
                           if "datavalue" in c["mainsnak"]]
            out[q] = {
                "netflix_ids": netflix_ids,
                "dates": entity_dates(e),
                "sitelinks": {k: v["title"] for k, v in e.get("sitelinks", {}).items()
                              if k in LANG_WIKIS},
            }
    return out


def fetch_type_roots(qids: list[str]) -> dict[str, list[str]]:
    """
    For each QID, which allowlist roots (from any category) it falls under.
    One SPARQL query with a P31/P279* path so subclasses count.
    """
    if not qids:
        return {}
    roots = {r for rs in TYPE_ROOTS.values() for r in rs}
    query = f"""
        SELECT DISTINCT ?item ?root WHERE {{
          VALUES ?item {{ {' '.join(f'wd:{q}' for q in qids)} }}
          VALUES ?root {{ {' '.join(f'wd:{r}' for r in roots)} }}
          ?item wdt:P31/wdt:P279* ?root .
        }}"""
    rows = config.http_get(config.WIKIDATA_SPARQL,
                           params={"query": query, "format": "json"}).json()["results"]["bindings"]
    out: dict[str, list[str]] = {q: [] for q in qids}
    for b in rows:
        out[b["item"]["value"].rsplit("/", 1)[-1]].append(b["root"]["value"].rsplit("/", 1)[-1])
    return out


def lookup(title: str) -> dict:
    """Everything the matching rules need for one title, in cacheable form."""
    cands = search_candidates(title)
    ents = fetch_compact_entities(list(cands)) if cands else {}
    # Types for every candidate: Rule B needs them, and the contested-match
    # flag needs them even when Rule A decides the match.
    return {"candidates": cands, "entities": ents,
            "types": fetch_type_roots(list(cands)), "types_all": True}


def contested_rivals(qid: str, category: str, info: dict) -> list[str]:
    """
    For a Netflix-ID match: other candidates with an allowed type for the
    category whose newest date is later than the chosen item's newest date
    (or that have no date). These are newer namesakes, often a remake or a
    recent film without a Netflix ID on Wikidata yet, that may be the title
    that actually charted. The match is kept but flagged as contested.
    """
    ents, types = info["entities"], info["types"]
    allowed = set(TYPE_ROOTS[category])
    chosen_newest = max(ents[qid]["dates"], default="0000")
    return [q for q in info["candidates"]
            if q != qid and allowed & set(types.get(q, []))
            and max(ents[q]["dates"], default="9999") > chosen_newest]


# ---------------------------------------------------------------------------
# Matching rules
# ---------------------------------------------------------------------------

def tie_break(qids: list[str], ents: dict, window_end: date) -> tuple[str | None, str]:
    """Pick among several candidates by date. Returns (qid or None, explanation)."""
    dist: dict[str, int | None] = {}
    for q in qids:
        ds = [date.fromisoformat(d) for d in ents[q]["dates"]]
        dist[q] = min(abs((d - window_end).days) for d in ds) if ds else None
    undated = [q for q, v in dist.items() if v is None]
    dated = sorted((v, q) for q, v in dist.items() if v is not None)
    if undated:
        return None, (f"{len(qids)} candidates; undated item(s) {', '.join(undated)} "
                      "could be the right one, tie not safely breakable")
    if len(dated) > 1 and dated[0][0] == dated[1][0]:
        return None, f"{len(qids)} candidates tied on date"
    if dated[0][0] > TIEBREAK_MAX_YEARS * 365:
        return None, (f"{len(qids)} candidates; closest ({dated[0][1]}) is "
                      f"{dated[0][0] // 365} years from the window, likely an older namesake")
    return dated[0][1], f"date tie-break among {len(qids)} ({', '.join(qids)})"


def match(title: str, category: str, info: dict, window_end: date) -> tuple[str | None, str, str]:
    """Apply Rule A, then Rule B. Returns (qid or None, method, explanation)."""
    cands, ents, types = info["candidates"], info["entities"], info["types"]
    if not cands:
        return None, "none", "no Wikidata item with this label or alias"

    # Rule A: Netflix ID.
    with_nid = [q for q in cands if ents[q]["netflix_ids"]]
    if len(with_nid) == 1:
        return with_nid[0], "netflix_id", f"Netflix ID {ents[with_nid[0]]['netflix_ids'][0]}"
    if len(with_nid) > 1:
        q, why = tie_break(with_nid, ents, window_end)
        return q, "netflix_id_tiebreak" if q else "none", f"Netflix ID: {why}"

    # Rule B: exact label, type allowlist, then dates.
    labels = [q for q, how in cands.items() if how == "label"]
    if not labels:
        return None, "none", "alias match only and no Netflix ID"
    allowed = set(TYPE_ROOTS[category])
    survivors = [q for q in labels if allowed & set(types.get(q, []))]
    if not survivors:
        return None, "none", (f"{len(labels)} label match(es), none typed as "
                              f"{'/'.join(TYPE_ROOTS[category].values())}")
    if len(survivors) == 1:
        return survivors[0], "label_unique", "unique label + type match"
    q, why = tie_break(survivors, ents, window_end)
    return q, "label_tiebreak" if q else "none", why


# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    titles = pd.read_csv(config.TITLES_CSV)
    pairs = pd.read_csv(config.TITLE_MARKETS_CSV)
    window_end = pd.to_datetime(pd.read_csv(config.NETFLIX_6MKTS_CSV)["week"]).max().date()

    # Cache keyed by English title. Saved after every lookup so an
    # interrupted run resumes where it stopped.
    cache: dict = {}
    if config.WIKIDATA_CACHE_JSON.exists() and not args.refresh:
        cache = json.loads(config.WIKIDATA_CACHE_JSON.read_text(encoding="utf-8"))

    def save_cache() -> None:
        config.WIKIDATA_CACHE_JSON.write_text(
            json.dumps(cache, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")

    log_rows = []
    for i, t in enumerate(titles.itertuples(index=False), 1):
        info = cache.get(t.show_title)
        if info is None:
            info = cache[t.show_title] = lookup(t.show_title)
            save_cache()
            time.sleep(0.3)
        elif not info.get("types_all"):
            # Older cache entries only typed Rule B candidates; complete them.
            info["types"] = fetch_type_roots(list(info["candidates"]))
            info["types_all"] = True
            save_cache()
        qid, method, why = match(t.show_title, t.category, info, window_end)
        rivals = contested_rivals(qid, t.category, info) if method.startswith("netflix_id") else []
        log_rows.append({"title_id": t.title_id, "show_title": t.show_title,
                         "category": t.category, "n_markets": t.n_markets,
                         "candidates": len(info["candidates"]),
                         "qid": qid or "", "match_method": method, "result": why,
                         "contested": bool(rivals), "newer_rivals": " ".join(rivals)})
        if i % 25 == 0 or i == len(titles):
            print(f"  {i}/{len(titles)} titles processed")

    log = pd.DataFrame(log_rows)
    log.to_csv(config.MATCH_LOG_CSV, index=False)

    # Resolve each charted title-market pair to an article, or log the drop.
    map_rows, dropped_rows = [], []
    by_id = log.set_index("title_id")
    for p in pairs.itertuples(index=False):
        m = by_id.loc[p.title_id]
        base = {"title_id": p.title_id, "show_title": p.show_title, "category": p.category,
                "market": p.market, "lang": p.lang, "qid": m["qid"]}
        if not m["qid"]:
            dropped_rows.append({**base, "reason": f"title unmatched: {m['result']}"})
            continue
        article = cache[p.show_title]["entities"][m["qid"]]["sitelinks"].get(f"{p.lang}wiki")
        if article:
            map_rows.append({**base, "match_method": m["match_method"],
                             "contested": m["contested"], "article": article})
        else:
            dropped_rows.append({**base, "reason": f"no {p.lang}wiki sitelink"})

    pd.DataFrame(map_rows).to_csv(config.TITLE_ARTICLE_MAP_CSV, index=False)
    pd.DataFrame(dropped_rows).to_csv(config.DROPPED_PAIRS_CSV, index=False)

    print(f"\nMatched {(log['qid'] != '').sum()}/{len(log)} titles")
    print(log["match_method"].value_counts().to_string())
    print(f"Netflix-ID matches flagged as contested (newer same-type namesake exists): "
          f"{int(log['contested'].sum())}")
    print(f"{len(map_rows)} of {len(pairs)} charted title-market pairs have an article; "
          f"{len(dropped_rows)} dropped")


if __name__ == "__main__":
    main()
