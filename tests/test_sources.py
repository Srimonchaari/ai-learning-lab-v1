from pathlib import Path
import feedparser

from src.sources import FeedItem, filter_and_dedupe


def test_filter_and_dedupe_matches_keywords_and_removes_duplicates():
    items = [
        FeedItem(
            title="Embeddings for semantic search",
            link="https://example.com/embeddings",
            published=None,
            summary="Learn embeddings and vector search basics.",
            source_feed="sample",
        ),
        FeedItem(
            title="Unrelated Kubernetes post",
            link="https://example.com/k8s",
            published=None,
            summary="Not about AI systems engineering.",
            source_feed="sample",
        ),
        FeedItem(
            title="Embeddings for semantic search",
            link="https://example.com/embeddings",
            published=None,
            summary="Duplicate link item.",
            source_feed="sample",
        ),
    ]

    filtered = filter_and_dedupe(items, keywords=["embeddings", "vector"], max_results=20)
    assert len(filtered) == 1
    assert filtered[0].link == "https://example.com/embeddings"


def test_fixture_rss_parses(tmp_path: Path):
    # sanity check: feedparser can parse our fixture (useful for future mocking)
    xml = (Path("tests") / "fixtures" / "sample_rss.xml").read_text(encoding="utf-8")
    p = tmp_path / "feed.xml"
    p.write_text(xml, encoding="utf-8")

    d = feedparser.parse(str(p))
    assert len(d.entries) >= 2
    assert d.entries[0].title
    assert d.entries[0].link
