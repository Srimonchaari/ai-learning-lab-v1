from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from progress import load_progress, save_progress, completed_ids, mark_completed
from roadmap import load_roadmap, flatten_concepts, select_next_concept
from sources import fetch_feed_items, filter_and_dedupe


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROADMAP_PATH = PROJECT_ROOT / "roadmap.yaml"
PROGRESS_PATH = PROJECT_ROOT / "data" / "progress.json"


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


# ---------------- Feed packs ----------------
# Strict: minimal, stable sources. Broader: more discovery sources.
# Note: RSS endpoints can change. If some feeds fail later, we’ll move these to a feeds.yaml.

FOUNDATIONS_STRICT = [
    "https://www.geeksforgeeks.org/feed/",
    "https://realpython.com/atom.xml",
]

FOUNDATIONS_BROADER = FOUNDATIONS_STRICT + [
    "https://www.python.org/blogs/rss/",
    "https://github.blog/feed/",
]

AI_STRICT = [
    "https://aws.amazon.com/blogs/machine-learning/feed/",
    "https://cloud.google.com/blog/topics/ai-ml/rss",
    "http://export.arxiv.org/rss/cs.AI",
    "http://export.arxiv.org/rss/cs.LG",
    "http://export.arxiv.org/rss/cs.CL",
]

AI_BROADER = AI_STRICT + [
    "https://huggingface.co/blog/feed.xml",
    "https://pytorch.org/blog/rss.xml",
    "https://github.blog/feed/",
]


def feeds_for(category: str, mode: str) -> List[str]:
    cat = (category or "").lower()
    m = mode.lower()

    if cat in {"foundations", "engineering_foundations"}:
        return FOUNDATIONS_STRICT if m == "strict" else FOUNDATIONS_BROADER

    # Default to AI pack for llm/rag/production/safety/deployment in V1
    return AI_STRICT if m == "strict" else AI_BROADER


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="AI Learning Lab V1 runner")
    p.add_argument("--mode", choices=["strict", "broader"], default="strict")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--mark-done", action="store_true")
    p.add_argument("--max-age-days", type=int, default=30)
    p.add_argument("--limit-per-feed", type=int, default=15)
    p.add_argument("--max-results", type=int, default=10)
    p.add_argument("--log-level", default="INFO")
    p.add_argument("--list-feeds", action="store_true")
    return p.parse_args(argv)


def fetch_candidates_with_fallback(
    keywords: List[str],
    category: str,
    mode: str,
    limit_per_feed: int,
    max_age_days: int,
    max_results: int,
) -> Tuple[List[str], List, str]:
    """
    Strategy:
      1) category feeds in selected mode
      2) if strict yields none -> category broader
      3) final fallback -> global broader AI feeds
    """
    # 1) chosen mode
    feeds1 = feeds_for(category, mode)
    items1 = fetch_feed_items(feeds=feeds1, limit_per_feed=limit_per_feed, max_age_days=max_age_days)
    cand1 = filter_and_dedupe(items1, keywords=keywords, max_results=max_results)
    if cand1:
        return feeds1, cand1, "category_primary"

    # 2) fallback to broader within category if strict
    if mode == "strict":
        feeds2 = feeds_for(category, "broader")
        items2 = fetch_feed_items(feeds=feeds2, limit_per_feed=limit_per_feed, max_age_days=max_age_days)
        cand2 = filter_and_dedupe(items2, keywords=keywords, max_results=max_results)
        if cand2:
            return feeds2, cand2, "category_fallback_broader"

    # 3) global fallback
    feeds3 = AI_BROADER
    items3 = fetch_feed_items(feeds=feeds3, limit_per_feed=limit_per_feed, max_age_days=max_age_days)
    cand3 = filter_and_dedupe(items3, keywords=keywords, max_results=max_results)
    return feeds3, cand3, "global_fallback"


def print_summary(concept: Dict, candidates: List) -> None:
    print("\n=== TODAY'S NODE ===")
    print(f"ID: {concept['id']}")
    print(f"Title: {concept['title']}")
    print(f"Level: {concept.get('level', '')}")
    print(f"Category: {concept.get('category', '')}")
    print(f"Mini Project: {concept.get('mini_project', '')}")

    print("\n=== SOURCE CANDIDATES (Filtered) ===")
    if not candidates:
        print("No candidates matched keywords.")
        print("Action: refine keywords in roadmap.yaml or use broader mode.")
        return

    for i, it in enumerate(candidates, start=1):
        print(f"{i}. {it.title}")
        print(f"   {it.link}")
        if it.published:
            print(f"   Published: {it.published.isoformat()}")
        print(f"   Feed: {it.source_feed}\n")


def main() -> None:
    args = parse_args(sys.argv[1:])
    setup_logging(args.log_level)

    logging.info("AI Learning Lab V1 starting")
    logging.info("Mode=%s dry_run=%s mark_done=%s", args.mode, args.dry_run, args.mark_done)

    try:
        roadmap = load_roadmap(ROADMAP_PATH)
        concepts = flatten_concepts(roadmap)

        progress = load_progress(PROGRESS_PATH)
        done = completed_ids(progress)

        next_concept = select_next_concept(concepts, done)
        keywords = list(next_concept.get("keywords", []))
        category = next_concept.get("category", "ai")

        if args.list_feeds:
            print("=== FEEDS (strict) ===")
            for f in feeds_for(category, "strict"):
                print("-", f)
            print("\n=== FEEDS (broader) ===")
            for f in feeds_for(category, "broader"):
                print("-", f)
            return

        logging.info("Selected concept: %s | %s", next_concept["id"], next_concept["title"])
        logging.info("Category=%s Keywords=%s", category, keywords)

        feeds_used, candidates, strategy = fetch_candidates_with_fallback(
            keywords=keywords,
            category=category,
            mode=args.mode,
            limit_per_feed=args.limit_per_feed,
            max_age_days=args.max_age_days,
            max_results=args.max_results,
        )
        logging.info("Fetch strategy=%s feeds=%d candidates=%d", strategy, len(feeds_used), len(candidates))

        print_summary(next_concept, candidates)

        if args.dry_run:
            logging.info("Dry run: no progress changes.")
            return

        if args.mark_done:
            mark_completed(progress, next_concept["id"])
            save_progress(PROGRESS_PATH, progress)
            logging.info("Marked completed and saved progress: %s", PROGRESS_PATH)

        logging.info("V1 run completed successfully")

    except Exception:
        logging.exception("Fatal error in V1 runner")
        sys.exit(1)


if __name__ == "__main__":
    main()
