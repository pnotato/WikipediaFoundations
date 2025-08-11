# scripts/wikidata_api.py

import os
import time
from typing import List, Dict, Set
import requests
import re

def _get_page_url(title: str) -> str:
    return f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"

def _load_visited_titles(visited_path: str) -> Set[str]:
    if not os.path.exists(visited_path):
        return set()
    with open(visited_path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}

def _sum_pageviews(pv_data) -> int:
    # On Wikimedia, prop=pageviews returns a dict of YYYY-MM-DD -> count
    if isinstance(pv_data, dict):
        return sum(v for v in pv_data.values() if isinstance(v, int))
    # Fallback (rare) if an array of {views: int} is returned
    if isinstance(pv_data, list):
        total = 0
        for item in pv_data:
            if isinstance(item, dict):
                v = item.get("views")
                if isinstance(v, int):
                    total += v
        return total
    return 0

# Regex for Vital Articles categories on Talk pages, e.g.,
# "Category:Wikipedia level-3 vital articles" or
# "Category:Wikipedia level-2 vital articles in Philosophy and religion"
VA_RE = re.compile(r"^Category:Wikipedia level-(\d)\s+vital articles(?:\b.*)?$", re.IGNORECASE)

def _fetch_vital_level(session: requests.Session, api: str, title: str) -> str:
    """
    Return '1'..'5' if the page has a Vital Articles level on its Talk page, else ''.
    Looks at Talk:<title> categories via MediaWiki API.
    """
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "redirects": 1,
        "converttitles": 1,
        "prop": "categories",
        "cllimit": "max",
        "titles": f"Talk:{title}",
    }
    try:
        r = session.get(api, params=params, timeout=(5, 20))
        r.raise_for_status()
        data = r.json()
    except Exception:
        return ""

    pages = (data.get("query", {}) or {}).get("pages", []) or []
    if not pages:
        return ""

    cats = pages[0].get("categories", []) or []
    for c in cats:
        name = c.get("title", "")
        m = VA_RE.match(name)
        if m:
            return m.group(1)
    return ""

def fetch_api_rows_for_titles(
    session: requests.Session,
    api: str,
    titles: List[str],
    visited_path: str,
    views_days: int = 30,
    max_link_cont: int = 5,
) -> List[Dict]:
    """
    For each title not present in visited.txt:
      - Single-title query to get earliest revision timestamp, page length, pageviews
      - Count links with limited continuation
    Returns list of dicts with keys: page_title, page_url, length_bytes, links_count, created_ts, views_30d, vital_level
    """
    visited = _load_visited_titles(visited_path)
    out: List[Dict] = []

    for orig_title in titles:
        if orig_title in visited:
            continue

        # Single-title base query
        params = {
            "action": "query",
            "format": "json",
            "titles": orig_title,
            "prop": "revisions|info|links|pageviews",
            "rvprop": "timestamp",
            "rvlimit": 1,
            "rvdir": "newer",      # earliest revision
            "inprop": "url",
            "plnamespace": 0,
            "pllimit": "max",
            "pvipdays": str(min(max(views_days, 1), 60)),
            "redirects": 1,
            "converttitles": 1,
        }

        r = session.get(api, params=params, timeout=(5, 20))
        r.raise_for_status()
        data = r.json()

        pages = (data.get("query", {}) or {}).get("pages", {}) or {}
        # Grab the single page object (there should be exactly one)
        page = next(iter(pages.values()), None)

        if not isinstance(page, dict) or page.get("missing") is not None:
            # Page missing/invalid: emit empty row with canonicalized title if available
            canon = page.get("title") if isinstance(page, dict) else orig_title
            out.append({
                "page_title": canon or orig_title,
                "page_url": _get_page_url(canon or orig_title),
                "length_bytes": None,
                "links_count": None,
                "created_ts": None,
                "views_30d": None,
                "vital_level": None,
            })
            continue

        canon_title = page.get("title") or orig_title
        length_bytes = page.get("length") if isinstance(page.get("length"), int) else None

        # Earliest revision timestamp
        revs = page.get("revisions") or []
        created_ts = revs[0]["timestamp"] if revs else None

        # First batch of links + follow plcontinue a few times to increase coverage
        links_count = len(page.get("links") or [])
        cont = data.get("continue", {}) or {}
        plcontinue = cont.get("plcontinue")
        cont_token = cont.get("continue")
        tries = 0
        while plcontinue and tries < max_link_cont:
            tries += 1
            params_cont = dict(params)
            params_cont["plcontinue"] = plcontinue
            params_cont["continue"] = cont_token
            r2 = session.get(api, params=params_cont, timeout=(5, 20))
            r2.raise_for_status()
            d2 = r2.json()
            pages2 = (d2.get("query", {}) or {}).get("pages", {}) or {}
            page2 = next(iter(pages2.values()), {})
            links_count += len(page2.get("links") or [])
            cont = d2.get("continue", {}) or {}
            plcontinue = cont.get("plcontinue")
            cont_token = cont.get("continue")
            time.sleep(0.1)

        # Pageviews sum over window
        views_30d = _sum_pageviews(page.get("pageviews"))

        # Vital Articles level from Talk page categories ('', if none)
        vital_level = _fetch_vital_level(session, api, canon_title)

        out.append({
            "page_title": canon_title,
            "page_url": _get_page_url(canon_title),
            "length_bytes": length_bytes,
            "links_count": links_count,
            "created_ts": created_ts,
            "views_30d": views_30d,
            "vital_level": vital_level,
        })

        time.sleep(0.1)

    return out