def in_ignored_container(tag) -> bool:
    """Return True if `tag` is inside containers we want to ignore (hatnotes, notes, sidebars, references, etc.)."""
    for parent in tag.parents:
        # Skip links in tables/infoboxes, spans (IPA/pronunciation), figcaptions, and citation superscripts
        if parent.name in ("table", "span") or parent.name == "figcaption":
            return True
        if parent.name == "sup" and "reference" in (parent.get("class") or []):
            return True
        # Skip anything with classes that typically denote notes/hatnotes/sidebars/navboxes/thumbnails
        classes = parent.get("class") or []
        joined = " ".join(classes)
        if any(k in joined for k in ("hatnote", "note", "sidebar", "mbox", "navbox", "thumb", "vertical-navbox")):
            return True
        # Some pages mark notes with a role
        if parent.get("role") == "note":
            return True
    return False
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://en.wikipedia.org"
RANDOM = "https://en.wikipedia.org/wiki/Special:Random"
PHILOSOPHY = "https://en.wikipedia.org/wiki/Philosophy"
PHILOSOPHICAL = "https://en.wikipedia.org/wiki/Philosophical"

HEADERS = {"User-Agent": "WikiPaths/0.1 (student project; email@example.com)"}
MAX_STEPS = 100
SLEEP = 0.5  # be polite

def strip_parentheses(html_bytes: bytes) -> bytes:
    """Remove text inside parentheses in the HTML text content (not inside tags)."""
    s = html_bytes.decode("utf-8", errors="ignore")
    out, paren, in_tag = [], 0, False
    for ch in s:
        if ch == "<": in_tag = True
        if not in_tag:
            if ch == "(": paren += 1
            if paren == 0: out.append(ch)
            if ch == ")" and paren > 0: paren -= 1
        else:
            out.append(ch)
        if ch == ">": in_tag = False
    return "".join(out).encode("utf-8")

def good_article_href(href: str | None) -> bool:
    if not href: return False
    if not href.startswith("/wiki/"): return False
    # skip non-article namespaces and main page
    bad_prefixes = ("File:", "Wikipedia:", "Portal:", "Special:", "Help:",
                    "Template:", "Template_talk:", "Talk:", "Category:", "Main_Page")
    return not any(href[6:].startswith(p) for p in bad_prefixes)  # strip "/wiki/"

def normalize_url(u: str) -> str:
    # Strip fragment and trailing slash; compare case-insensitively
    if not u:
        return u
    base = u.split('#')[0].rstrip('/')
    return base.lower()

def resolve_redirects(u: str) -> str:
    try:
        r = requests.get(u, headers=HEADERS, allow_redirects=True, timeout=15)
        return r.url
    except Exception:
        return u

def is_philosophy(u: str) -> bool:
    try:
        norm = normalize_url(resolve_redirects(u))
        targets = {normalize_url(PHILOSOPHY), normalize_url(PHILOSOPHICAL)}
        return norm in targets
    except Exception:
        return False

def first_link(url: str) -> str | None:
    """Return absolute URL of the first valid link in main paragraphs, else None."""
    r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=15)
    r.raise_for_status()
    cleaned = strip_parentheses(r.content)
    soup = BeautifulSoup(cleaned, "html.parser")

    # main article content paragraphs
    content = soup.find("div", id="mw-content-text")
    if not content: return None
    for p in content.select("div.mw-parser-output > p"):
        # For each anchor in document order
        for a in p.find_all("a", recursive=True):
            # --- BEGIN: Skip links inside unmatched parentheses ---
            # Get the HTML of the paragraph up to this anchor tag
            para_html = p.decode_contents()
            a_html = a.decode()
            idx = para_html.find(a_html)
            if idx != -1:
                up_to_link = para_html[:idx]
                # Remove tags to count parentheses only in visible text
                import re
                up_to_link_text = re.sub("<[^>]+>", "", up_to_link)
                l_count = up_to_link_text.count("(")
                r_count = up_to_link_text.count(")")
                if l_count > r_count:
                    continue  # skip this link, it's inside parentheses
            # --- END: Skip links inside unmatched parentheses ---
            # skip links inside hatnotes/notes/sidebars/tables/spans/citations, etc.
            if in_ignored_container(a):
                continue
            href = a.get("href")
            if good_article_href(href):
                # Extract the surrounding sentence
                para_text = p.get_text()
                link_text = a.get_text()
                link_pos = para_text.find(link_text)
                if link_pos == -1:
                    link_sentence = para_text.strip()
                else:
                    # Find sentence boundaries using . ? !
                    start = max(para_text.rfind('.', 0, link_pos),
                                para_text.rfind('?', 0, link_pos),
                                para_text.rfind('!', 0, link_pos))
                    end = min((para_text.find('.', link_pos),
                               para_text.find('?', link_pos),
                               para_text.find('!', link_pos)))
                    # If no punctuation found, use start/end of paragraph
                    if start == -1:
                        start = 0
                    else:
                        start += 1
                    if end == -1:
                        end = len(para_text)
                    link_sentence = para_text[start:end].strip()
                return urljoin(BASE, href), link_sentence
    # very basic fallback: try any link in content that looks like an article, but skip ignored containers
    for a in content.find_all("a"):
        if in_ignored_container(a):
            continue
        href = a.get("href")
        if good_article_href(href):
            # Extract the surrounding sentence for fallback as well
            p = a.find_parent("p")
            if p:
                para_text = p.get_text()
                link_text = a.get_text()
                link_pos = para_text.find(link_text)
                if link_pos == -1:
                    link_sentence = para_text.strip()
                else:
                    start = max(para_text.rfind('.', 0, link_pos),
                                para_text.rfind('?', 0, link_pos),
                                para_text.rfind('!', 0, link_pos))
                    end = min((para_text.find('.', link_pos),
                               para_text.find('?', link_pos),
                               para_text.find('!', link_pos)))
                    if start == -1:
                        start = 0
                    else:
                        start += 1
                    if end == -1:
                        end = len(para_text)
                    link_sentence = para_text[start:end].strip()
            else:
                link_sentence = ""
            return urljoin(BASE, href), link_sentence
    return None

def title_of(url: str) -> str:
    return url.split("/wiki/")[-1].replace("_", " ")

def steps_to_philosophy(start: str | None = None) -> tuple[int, str, list[str]]:
    """Follow first links; return (steps, stop_reason, path)."""
    url = start or requests.get(RANDOM, headers=HEADERS, allow_redirects=True, timeout=15).url
    url = resolve_redirects(url)

    # Fetch and print initial paragraph text for inspection
    r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "html.parser")
    content_div = soup.find("div", class_="mw-parser-output")
    if content_div:
        paragraphs = content_div.find_all("p", limit=3)
        combined_text = " ".join(p.get_text() for p in paragraphs)
        print(f"Initial paragraphs preview (first ~300 chars):\n{combined_text[:300]}\n")

    seen = set()
    path = [url]

    for step in range(MAX_STEPS):
        print(f"Step {step}: {title_of(url)} | {url}")
        # Resolve the current page's redirects and check against Philosophy
        current_resolved = resolve_redirects(url)
        if current_resolved != url:
            url = current_resolved
            path[-1] = url
        if is_philosophy(url):
            return step, "reached_philosophy", path
        if url in seen:
            return step, "loop_detected", path
        seen.add(url)

        result = first_link(url)
        if not result:
            return step, "dead_end", path
        nxt, sentence = result
        # Resolve redirects on the next URL so we can detect Philosophy immediately
        resolved = resolve_redirects(nxt)
        if is_philosophy(resolved):
            path.append(resolved)
            return step + 1, "reached_philosophy", path
        path.append(resolved)
        url = resolved
        time.sleep(SLEEP)

    return len(path) - 1, "max_steps_exceeded", path

if __name__ == "__main__":
    steps, reason, path = steps_to_philosophy()
    print(f"Start: {title_of(path[0])}")
    print(f"Steps: {steps} | Stop: {reason}")
    print("→ ".join(title_of(u) for u in path[:10]), "..." if len(path) > 10 else "")