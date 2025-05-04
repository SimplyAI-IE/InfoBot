import feedparser
import yaml
import time
from pathlib import Path
from typing import List, Dict

FEED_URL = "https://rss.app/feeds/1d2cJLp1b3BgSzQB.xml"
CACHE_PATH = Path(__file__).resolve().parent / "facebook_updates.yaml"
CACHE_TTL = 60 * 60  # 1 hour


def fetch_facebook_posts(force: bool = False) -> List[Dict[str, str]]:
    if not force and CACHE_PATH.exists():
        if time.time() - CACHE_PATH.stat().st_mtime < CACHE_TTL:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)

    feed = feedparser.parse(FEED_URL)
    posts = []

    for entry in feed.entries:
        posts.append(
            {
                "title": entry.title,
                "summary": entry.summary,
                "published": entry.published,
                "link": entry.link,
            }
        )

    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        yaml.dump(posts, f, allow_unicode=True)

    return posts
