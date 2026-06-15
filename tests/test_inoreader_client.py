from __future__ import annotations

import pytest

from newsroom.ingest.inoreader_client import (
    InoreaderClient,
    parse_inoreader_stream,
    parse_inoreader_subscriptions,
)


SUBSCRIPTION_PAYLOAD = {
    "subscriptions": [
        {
            "id": "feed/https://example.com/feed.xml",
            "title": "Example Feed",
            "categories": [{"label": "Tech"}],
            "url": "https://example.com/feed.xml",
            "htmlUrl": "https://example.com/",
            "iconUrl": "https://example.com/icon.png",
        }
    ]
}


def test_parse_inoreader_subscriptions_maps_source_feed_fields():
    sources = parse_inoreader_subscriptions(SUBSCRIPTION_PAYLOAD)
    source = sources[0]

    assert source.url == "https://example.com/feed.xml"
    assert source.name == "Example Feed"
    assert source.reader == "inoreader"
    assert source.reader_feed_id == "feed/https://example.com/feed.xml"
    assert source.html_url == "https://example.com/"
    assert source.icon_url == "https://example.com/icon.png"
    assert source.reader_categories == ["Tech"]
    assert source.tags == ["reader/tech"]


def test_parse_inoreader_stream_maps_article_fields_from_source_lookup():
    sources = parse_inoreader_subscriptions(SUBSCRIPTION_PAYLOAD)
    payload = {
        "items": [
            {
                "title": "Example Article",
                "published": 1779753600,
                "canonical": [{"href": "https://example.com/article"}],
                "summary": {"content": "<p>Article summary</p>"},
                "origin": {
                    "streamId": "feed/https://example.com/feed.xml",
                    "title": "Fallback Feed",
                },
            }
        ]
    }

    articles = parse_inoreader_stream(
        payload,
        sources=sources,
        fetched_at="2026-05-26T10:00:00+00:00",
    )
    article = articles[0]

    assert article.title == "Example Article"
    assert article.published_at == "2026-05-26T00:00:00+00:00"
    assert article.source_name == "Example Feed"
    assert article.source_url == "https://example.com/feed.xml"
    assert article.summary == "<p>Article summary</p>"
    assert article.tags == ["reader/tech"]


def test_inoreader_client_requires_env_token(monkeypatch):
    client = InoreaderClient(enabled=True, access_token_env="NEWSROOM_TEST_TOKEN")
    monkeypatch.delenv("NEWSROOM_TEST_TOKEN", raising=False)

    with pytest.raises(ValueError, match="NEWSROOM_TEST_TOKEN"):
        client.load_subscription_sources()
