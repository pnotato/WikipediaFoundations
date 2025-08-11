import os
import csv
import time
import requests
import sys
from datetime import datetime
from typing import List

from wikidata_html import steps_to_philosophy, title_of
from wikidata_api import fetch_api_rows_for_titles

WIKI_API = "https://en.wikipedia.org/w/api.php"

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CSV_DIR = DATA_DIR
LOG_DIR = os.path.join(DATA_DIR, "logs")
os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

HYPERLINK_CSV = os.path.join(CSV_DIR, "hyperlink_data.csv")
API_CSV = os.path.join(CSV_DIR, "api_data.csv")
VISITED_TXT = os.path.join(LOG_DIR, "visited.txt")
OUTPUT_TXT = os.path.join(LOG_DIR, "output.txt")

MAX_STEPS = 100
DELAY = 0.5

def init_session() -> requests.Session:
    s = requests.Session()
    return s

def append_text(path: str, text: str) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(text)

def write_hyperlink_rows(path_urls: List[str], stop_reason: str, run_id: int):
    header = ["run_id","steps_total","page_title","page_url","stop_reason","links_away"]
    steps_total = len(path_urls) - 1
    reached = (stop_reason == "reached_philosophy")
    rows = []
    for i, u in enumerate(path_urls):
        links_away = (steps_total - i) if reached else "n/a"
        rows.append([run_id, steps_total, title_of(u), u, stop_reason, links_away])
    file_exists = os.path.exists(HYPERLINK_CSV)
    with open(HYPERLINK_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(header)
        w.writerows(rows)

def write_api_rows(rows: List[dict], run_id: int):
    header = ["run_id","page_title","page_url","length_bytes","links_count","created_ts","views_30d"]
    file_exists = os.path.exists(API_CSV)
    with open(API_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(header)
        for r in rows:
            w.writerow([run_id, r["page_title"], r["page_url"], r["length_bytes"], r["links_count"], r["created_ts"], r["views_30d"]])

def log_run(run_id: int, start_url: str, stop_reason: str, path_urls: List[str]):
    ts = datetime.now().isoformat(timespec="seconds")
    lines = [
        f"RUN {run_id} | {ts}",
        f"Start: {title_of(start_url)} | {start_url}",
        *[f"Step {i}: {title_of(u)} | {u}" for i, u in enumerate(path_urls)],
        f"END: reason={stop_reason}; steps={len(path_urls)-1}",
        f"Final: {title_of(path_urls[-1])} | {path_urls[-1]}",
        "\n"
    ]
    append_text(OUTPUT_TXT, "\n".join(lines))

def append_visited_titles(titles: List[str]):
    existing = set()
    if os.path.exists(VISITED_TXT):
        with open(VISITED_TXT, "r", encoding="utf-8") as f:
            for line in f:
                t = line.strip()
                if t:
                    existing.add(t)
    new_titles = [t for t in titles if t not in existing]
    if new_titles:
        with open(VISITED_TXT, "a", encoding="utf-8") as f:
            for t in new_titles:
                f.write(t + "\n")

def run_once(session: requests.Session, run_id: int, start_url: str | None = None):
    result = steps_to_philosophy(session, run_id, DATA_DIR, start_url, MAX_STEPS, DELAY)
    path_urls = result["path_urls"]
    stop_reason = result["stop_reason"]

    titles = [title_of(u) for u in path_urls]
    api_rows = fetch_api_rows_for_titles(session, WIKI_API, titles, VISITED_TXT)
    write_api_rows(api_rows, run_id)

    write_hyperlink_rows(path_urls, stop_reason, run_id)
    log_run(run_id, path_urls[0], stop_reason, path_urls)
    append_visited_titles(titles)

def next_run_id() -> int:
    if not os.path.exists(OUTPUT_TXT):
        return 1
    n = 0
    with open(OUTPUT_TXT, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("RUN "):
                n += 1
    return n + 1

if __name__ == "__main__":
    session = init_session()
    if len(sys.argv) < 2:
        print("usage: python3 wikidata.py. <number of runs>")
        sys.exit(1)
    runs = int(sys.argv[1])
    start = os.getenv("START_URL") or None
    for _ in range(runs):
        run_id = next_run_id()
        run_once(session, run_id, start)
        time.sleep(0.2)
        append_text(OUTPUT_TXT, f"=== Finished Run: {run_id} ===\n")