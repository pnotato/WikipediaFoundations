#!/usr/bin/env python3
import csv
import re
import time
import requests
from urllib.parse import unquote

API_URL = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "CMPT353-Foundations/0.1 (contact: your_email@example.com)"

# Regex to detect VA categories on talk pages:
# e.g., "Category:Wikipedia level-3 vital articles"
#       "Category:Wikipedia level-2 vital articles in Philosophy and religion"
VA_RE = re.compile(r"^Category:Wikipedia level-(\d)\s+vital articles(?:\b.*)?$", re.IGNORECASE)

def fetch_vital_level(title: str) -> str:
    """
    Return '1'..'5' if the page has a Vital Articles level on its Talk page, else ''.
    """
    # Some titles in your CSV may be percent-encoded (e.g., "%C3%89mile Cornic")
    # Normalize to a clean title for the API.
    clean_title = unquote(title).strip()

    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "redirects": 1,
        "converttitles": 1,
        "prop": "categories",
        "cllimit": "max",
        "titles": f"Talk:{clean_title}",
    }
    try:
        r = requests.get(API_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return ""

    pages = data.get("query", {}).get("pages", [])
    if not pages:
        return ""

    cats = pages[0].get("categories", []) or []
    for c in cats:
        name = c.get("title", "")
        m = VA_RE.match(name)
        if m:
            return m.group(1)  # '1'..'5'
    return ""

def main(in_csv="../data/api_data.csv", out_csv="../data/api_data_with_vital.csv", sleep_sec=1):
    with open(in_csv, newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = list(reader.fieldnames)
        if "vital_level" not in fieldnames:
            fieldnames.append("vital_level")

        rows = list(reader)

    # Query and append
    for i, row in enumerate(rows, 1):
        if i < 1000:
            continue
        if i >= 3152:
            break
        title = row.get("page_title", "").strip()
        if not title:
            row["vital_level"] = ""
            continue

        level = fetch_vital_level(title)
        row["vital_level"] = level
        # Gentle throttle to be nice to the API
        print(i)
        time.sleep(sleep_sec)

    # Write output with the new column at the end
    with open(out_csv, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done. Wrote {len(rows)} rows to {out_csv}")

if __name__ == "__main__":
    # Adjust paths if your CSV lives elsewhere.
    main()