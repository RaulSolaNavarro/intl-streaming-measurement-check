"""
Step 03: map each selected title to its Wikipedia article in each language.

Input:  data/processed/selected_titles.csv
Output: data/processed/title_article_map.csv   (title_id, show_title, qid, market, lang, article)
        data/logs/wikidata_match_log.csv        (one row per title: how the match went)
        data/logs/dropped_pairs.csv             (title-market pairs with no usable article)

No translated titles are typed by hand. The English Netflix title is used
only to find the Wikidata item. The per-language article names come from
that item's sitelinks.

Matching rules, in order:
  1. Search Wikidata for the English title (wbsearchentities, up to 200 hits).
  2. Keep items whose English label equals the Netflix title, ignoring case,
     curly vs straight quotes, and repeated whitespace.
  3. Keep items whose type (P31, following subclass-of P279 upward) falls
     under the allowlist for the Netflix category:
        Films -> film (Q11424) or television special (Q1261214)
        TV    -> television program (Q15416), which covers series,
                 miniseries, anime, reality shows, and so on.
  4. One survivor is a match. Several survivors: pick the one whose closest
     publication date (P577) or start time (P580) is nearest to the end of
     the Netflix window. Drop the title and log it when:
       - nothing survives step 3,
       - any survivor has no date (it could be the right item, so the tie
         can't be broken safely),
       - two survivors are equally close, or
       - the winner's nearest date is more than TIEBREAK_MAX_YEARS from the
         window end. This catches the case where the Netflix title is a new
         release with no Wikidata item yet, and the "closest" candidate is an
         older namesake.

There is no hard date filter on a unique match, because long-running series
can have start dates many years before the window. Dates only decide ties.
"""

from __future__ import annotations

import re
import time
import unicodedata
from datetime import date

import pandas as pd

import config

# Type allowlist, keyed by Netflix category. Values are Wikidata class QIDs;
# an item qualifies if any of its P31 classes is one of these or a subclass.
TYPE_ROOTS = {
    "Films": {"Q11424": "film", "Q1261214": "television special"},
    "TV": {"Q15416": "television program"},
}

SEARCH_PAGE = 50   # wbsearchentities maximum page size
SEARCH_MAX = 200   # stop paging after this many hits

# In a tie-break, the winning candidate's nearest date must be within this
# many years of the window end, or the tie counts as unresolved.
TIEBREAK_MAX_YEARS = 2


def normalize(label: str) -> str:
    """Case-fold and tidy a title so trivial formatting differences don't block a match."""
    s = unicodedata.normalize("NFKC", label)
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"\s+", " ", s).strip()
    return s.casefold()


def search_label_matches(title: str) -> list[str]:
    """Return QIDs whose English label exactly matches the title (after normalize)."""
    target = normalize(title)
    qids: list[str] = []
    offset = 0
    while offset < SEARCH_MAX:
        resp = config.http_get(config.WIKIDATA_API, params={
            "action": "wbsearchentities", "search": title, "language": "en",
            "uselang": "en", "type": "item", "limit": SEARCH_PAGE,
            "continue": offset, "format": "json",
        })
        data = resp.json()
        for hit in data.get("search", []):
            # `label` is the item's English label. Aliases are ignored on purpose.
            if normalize(hit.get("label", "")) == target:
                qids.append(hit["id"])
        if "search-continue" not in data:
            break
        offset = data["search-continue"]
        time.sleep(0.2)
    return qids


def allowed_types(qids: list[str], roots: dict[str, str]) -> dict[str, set[str]]:
    """
    For each QID, return the allowlist roots it falls under (empty set if none).
    Uses one SPARQL query with a P31/P279* path so subclasses count.
    """
    if not qids:
        return {}
    values_items = " ".join(f"wd:{q}" for q in qids)
    values_roots = " ".join(f"wd:{r}" for r in roots)
    query = f"""
        SELECT DISTINCT ?item ?root WHERE {{
          VALUES ?item {{ {values_items} }}
          VALUES ?root {{ {values_roots} }}
          ?item wdt:P31/wdt:P279* ?root .
        }}"""
    resp = config.http_get(config.WIKIDATA_SPARQL, params={"query": query, "format": "json"})
    out: dict[str, set[str]] = {q: set() for q in qids}
    for b in resp.json()["results"]["bindings"]:
        item = b["item"]["value"].rsplit("/", 1)[-1]
        root = b["root"]["value"].rsplit("/", 1)[-1]
        out[item].add(root)
    return out


def get_entities(qids: list[str]) -> dict[str, dict]:
    """Fetch claims and sitelinks for up to 50 QIDs at a time."""
    out: dict[str, dict] = {}
    for i in range(0, len(qids), 50):
        resp = config.http_get(config.WIKIDATA_API, params={
            "action": "wbgetentities", "ids": "|".join(qids[i:i + 50]),
            "props": "claims|sitelinks", "format": "json",
        })
        out.update(resp.json()["entities"])
    return out


def entity_dates(entity: dict) -> list[date]:
    """All P577 (publication date) and P580 (start time) values as dates."""
    dates: list[date] = []
    for prop in ("P577", "P580"):
        for claim in entity.get("claims", {}).get(prop, []):
            try:
                t = claim["mainsnak"]["datavalue"]["value"]["time"]  # e.g. "+2022-02-11T00:00:00Z"
            except KeyError:
                continue  # "unknown value" or "no value" snaks
            m = re.match(r"^\+?(\d{4})-(\d{2})-(\d{2})", t)
            if m:
                y, mo, d = (int(x) for x in m.groups())
                # Year-only precision is stored with month/day 00.
                dates.append(date(y, max(mo, 1), max(d, 1)))
    return dates


def main() -> None:
    titles = pd.read_csv(config.SELECTED_TITLES_CSV)
    netflix = pd.read_csv(config.NETFLIX_6MKTS_CSV)
    window_end = pd.to_datetime(netflix["week"]).max().date()

    log_rows, map_rows, dropped_rows = [], [], []

    for t in titles.itertuples(index=False):
        roots = TYPE_ROOTS[t.category]
        label_hits = search_label_matches(t.show_title)
        types = allowed_types(label_hits, roots)
        survivors = [q for q in label_hits if types.get(q)]
        entities = get_entities(survivors) if survivors else {}

        chosen, reason = None, ""
        if not label_hits:
            reason = "no Wikidata item with this exact English label"
        elif not survivors:
            reason = f"{len(label_hits)} label match(es), none typed as {'/'.join(roots.values())}"
        elif len(survivors) == 1:
            chosen, reason = survivors[0], "unique match"
        else:
            # Tie-break on the date closest to the end of the Netflix window.
            dist = {}
            for q in survivors:
                ds = entity_dates(entities[q])
                dist[q] = min(abs((d - window_end).days) for d in ds) if ds else None
            dated = sorted((v, q) for q, v in dist.items() if v is not None)
            undated = [q for q, v in dist.items() if v is None]
            if undated:
                reason = (f"{len(survivors)} candidates; undated item(s) {', '.join(undated)} "
                          "could be the right one, tie not safely breakable")
            elif len(dated) > 1 and dated[0][0] == dated[1][0]:
                reason = f"{len(survivors)} candidates tied on date"
            elif dated[0][0] > TIEBREAK_MAX_YEARS * 365:
                reason = (f"{len(survivors)} candidates; closest ({dated[0][1]}) is "
                          f"{dated[0][0] // 365} years from the window, likely an older namesake")
            else:
                chosen = dated[0][1]
                reason = f"date tie-break among {len(survivors)} candidates ({', '.join(survivors)})"

        log_rows.append({
            "title_id": t.title_id, "show_title": t.show_title, "category": t.category,
            "label_matches": len(label_hits), "type_ok": len(survivors),
            "qid": chosen or "", "result": reason,
        })
        print(f"{t.title_id} {t.show_title!r}: {chosen or 'DROPPED'} ({reason})")

        # Build the per-market article list (or drop every market for this title).
        sitelinks = entities[chosen].get("sitelinks", {}) if chosen else {}
        for market, lang in config.MARKETS.items():
            link = sitelinks.get(f"{lang}wiki")
            if chosen and link:
                map_rows.append({
                    "title_id": t.title_id, "show_title": t.show_title, "category": t.category,
                    "qid": chosen, "market": market, "lang": lang, "article": link["title"],
                })
            else:
                dropped_rows.append({
                    "title_id": t.title_id, "show_title": t.show_title, "market": market,
                    "lang": lang, "qid": chosen or "",
                    "reason": f"no {lang}wiki sitelink" if chosen else f"title unmatched: {reason}",
                })
        time.sleep(0.5)

    pd.DataFrame(log_rows).to_csv(config.MATCH_LOG_CSV, index=False)
    pd.DataFrame(map_rows).to_csv(config.TITLE_ARTICLE_MAP_CSV, index=False)
    pd.DataFrame(dropped_rows, columns=["title_id", "show_title", "market", "lang", "qid", "reason"]
                 ).to_csv(config.DROPPED_PAIRS_CSV, index=False)
    print(f"\nMatched {sum(1 for r in log_rows if r['qid'])}/{len(log_rows)} titles; "
          f"{len(map_rows)} title-market pairs kept, {len(dropped_rows)} dropped")


if __name__ == "__main__":
    main()
