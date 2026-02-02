from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Iterable, List, Optional, Set
import re

import feedparser


@dataclass(frozen=True)
class FeedItem:
    title: str
    link: str
    published: Optional[datetime]
    summary: str
    source_feed: str


DEFAULT_FEEDS = [
    "https://aws.amazon.com/blogs/machine-learning/feed/",
    "https://cloud.google.com/blog/topics/ai-ml/rss",
    # Add Azure feed if you want later; keep V1 small and stable
    # "https://azure.microsoft.com/en-us/blog/topics/ai-machine-learning/feed/",
    "http://export.arxiv.org/rss/cs.AI",
    "http://export.arxiv.org/rss/cs.LG",
    "http://export.arxiv.org/rss/cs.CL",
]


def _parse_datetime(entry) -> Optional[datetime]:
    # feedparser provides published_parsed as time.struct_time sometimes
    t = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if not t:
        return None
    # Convert struct_time to aware UTC datetime
    return datetime(*t[:6], tzinfo=timezone.utc)


def _matches_keywords(text: str, keywords: Iterable[str]) -> bool:
    text_l = text.lower()
    for kw in keywords:
        if re.search(r"\b" + re.escape(kw.lower()) + r"\b", text_l):
            return True
    return False


def fetch_feed_items(
    feeds: List[str] = DEFAULT_FEEDS,
    limit_per_feed: int = 10,
    max_age_days: int = 14,
) -> List[FeedItem]:
    """
    Fetch RSS items from curated feeds.
    Returns items within the max_age_days window when possible.
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=max_age_days)

    items: List[FeedItem] = []

    for feed_url in feeds:
        d = feedparser.parse(feed_url)
        for entry in d.entries[:limit_per_feed]:
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()
            summary = getattr(entry, "summary", "").strip()
            published = _parse_datetime(entry)

            # Prefer filtering by date when available
            if published and published < cutoff:
                continue

            if title and link:
                items.append(
                    FeedItem(
                        title=title,
                        link=link,
                        published=published,
                        summary=summary,
                        source_feed=feed_url,
                    )
                )

    return items


def filter_and_dedupe(
    items: List[FeedItem],
    keywords: List[str],
    max_results: int = 20,
) -> List[FeedItem]:
    """
    Keep only items that match keywords (title+summary).
    Deduplicate by link.
    """
    seen: Set[str] = set()
    out: List[FeedItem] = []

    for it in items:
        haystack = f"{it.title}\n{it.summary}"
        if not _matches_keywords(haystack, keywords):
            continue

        if it.link in seen:
            continue

        seen.add(it.link)
        out.append(it)

        if len(out) >= max_results:
            break

    return out
