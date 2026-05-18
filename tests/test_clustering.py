from __future__ import annotations

from newsroom.clustering.story_clusterer import StoryClusterer
from newsroom.store.models import Article


def _make_article(article_id_seed: str, title: str, source: str = "Example", source_type: str = "news") -> Article:
    return Article.create(
        url=f"https://example.com/{article_id_seed}",
        title=title,
        source_name=source,
        source_type=source_type,
        published_at="2026-05-18T01:00:00+00:00",
        fetched_at="2026-05-18T02:00:00+00:00",
    )


def test_similar_titles_form_one_cluster():
    articles = [
        _make_article("a", "Microsoft Copilot rolls out new search experience", source="Microsoft Blog", source_type="official"),
        _make_article("b", "Copilot search feature lands across Microsoft Office", source="The Verge"),
        _make_article("c", "Apple unveils new iPhone display technology", source="Apple Newsroom", source_type="official"),
    ]

    clusters = StoryClusterer(threshold=0.4).cluster(articles, "2026-05-18")

    copilot_cluster = next(c for c in clusters if any("copilot" in e for e in c.entities))
    assert len(copilot_cluster.article_ids) == 2
    assert {"microsoft", "copilot"}.issubset(set(copilot_cluster.entities))


def test_unrelated_articles_stay_separate():
    articles = [
        _make_article("a", "Microsoft Copilot rolls out new search experience"),
        _make_article("b", "Apple unveils new iPhone display technology"),
        _make_article("c", "TikTok announces new creator monetization rules"),
    ]

    clusters = StoryClusterer(threshold=0.4).cluster(articles, "2026-05-18")

    assert len(clusters) == 3
    for cluster in clusters:
        assert len(cluster.article_ids) == 1
