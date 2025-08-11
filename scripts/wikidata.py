# main function for collecting wikidata

import os
import csv
import wptools
import time
import requests
import dotenv
from bs4 import BeautifulSoup
from datetime import datetime

# Load .env at the very top before any os.getenv calls
dotenv.load_dotenv()


# User agent and API endpoint (from env or defaults)
USER_AGENT = os.getenv("WIKI_USER_AGENT", "WikiPaths/0.1 (contact@example.com)")
WIKI_API = os.getenv("WIKI_API", "https://en.wikipedia.org/w/api.php")

# Environment Variables (after dotenv loaded)
WIKI_BOT_USERNAME = os.getenv("WIKI_BOT_USERNAME")
WIKI_BOT_PASSWORD = os.getenv("WIKI_BOT_PASSWORD")

WIKI_BOT_USERNAME="Pnotato@cmpt_353_bot"
WIKI_BOT_PASSWORD="q0ng72q2g4gm7vu7rpfk4pp2u613voun"

# Definitions for the Wikipedia links we're going to hit
RANDOM = "https://en.wikipedia.org/wiki/Special:Random"
PHILOSOPHY = "https://en.wikipedia.org/wiki/Philosophy"
PHILOSOPHICAL = "https://en.wikipedia.org/wiki/Philosophical"

MAX_STEPS = 100
DELAY = 0.5 # so I don't get API banned

def mediawiki_login() -> requests.Session:
    
    if not WIKI_BOT_USERNAME or not WIKI_BOT_PASSWORD:
        raise RuntimeError("Bot username/password not set in .env (WIKI_BOT_USERNAME / WIKI_BOT_PASSWORD)")

    s = requests.Session()
    r1 = s.get(WIKI_API, params={
        "action": "query",
        "meta": "tokens",
        "type": "login",
        "format": "json",
    }, timeout=15)
    r1.raise_for_status()
    data1 = r1.json()
    login_token = data1.get("query", {}).get("tokens", {}).get("logintoken")
    if not login_token:
        raise RuntimeError(f"Failed to get login token: {data1}")

    r2 = s.post(WIKI_API, data={
        "action": "login",
        "lgname": WIKI_BOT_USERNAME,      
        "lgpassword": WIKI_BOT_PASSWORD,  
        "lgtoken": login_token,
        "format": "json",
    }, timeout=15)
    r2.raise_for_status()
    data2 = r2.json()
    result = (data2.get("login") or {}).get("result")
    if result != "Success":
        raise RuntimeError(f"Login failed: {data2}")

    return s


if __name__ == "__main__":
    print(mediawiki_login())