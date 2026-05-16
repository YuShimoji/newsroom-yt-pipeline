from __future__ import annotations

from newsroom.store.db import count_articles, list_articles_for_date, upsert_article
from newsroom.store.models import Article


def test_upsert_article_deduplicates_by_url(tmp_path):
    db_path = tmp_path / "newsroom.sqlite"
    article = Article.create(
        url="https://example.com/a",
        title="First Title",
        source_name="Example",
        published_at="2026-05-16T01:00:00+00:00",
        fetched_at="2026-05-16T02:00:00+00:00",
    )
    updated = Article.create(
        url="https://example.com/a",
        title="Updated Title",
        source_name="Example",
        published_at="2026-05-16T01:00:00+00:00",
        fetched_at="2026-05-16T03:00:00+00:00",
    )

    upsert_article(db_path, article)
    upsert_article(db_path, updated)

    assert count_articles(db_path) == 1
    articles = list_articles_for_date(db_path, "2026-05-16")
    assert len(articles) == 1
    assert articles[0].title == "Updated Title"

