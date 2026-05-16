from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from newsroom.config import load_source_feeds
from newsroom.ingest.inoreader_client import InoreaderClient
from newsroom.ingest.rss_client import RssClient
from newsroom.scoring.topic_scorer import TopicScorer
from newsroom.store.db import (
    DEFAULT_DB_PATH,
    init_db,
    list_articles_for_date,
    upsert_article,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="newsroom")
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="SQLite database path")
    parser.add_argument("--config", default="configs/sources.yml", help="sources.yml path")

    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch_parser = subparsers.add_parser("fetch", help="Fetch source feeds")
    fetch_parser.add_argument("--source", choices=["rss", "inoreader", "all"], default="rss")

    report_parser = subparsers.add_parser("report", help="Print candidate reports")
    report_group = report_parser.add_mutually_exclusive_group()
    report_group.add_argument("--today", action="store_true", help="Report for the local current date")
    report_group.add_argument("--date", help="Report date in YYYY-MM-DD format")

    return parser


def cmd_fetch(args: argparse.Namespace) -> int:
    db_path = Path(args.db)
    init_db(db_path)

    if args.source == "inoreader":
        client = InoreaderClient.from_config_path(args.config)
        print(client.describe_stub())
        return 2

    feeds = load_source_feeds(args.config)
    rss_feeds = [feed for feed in feeds if feed.enabled and feed.kind == "rss"]
    if not rss_feeds:
        print("No enabled RSS feeds found.")
        return 0

    client = RssClient()
    total_seen = 0
    total_stored = 0
    failures: list[str] = []

    for feed in rss_feeds:
        try:
            articles = client.fetch(feed)
        except Exception as exc:  # pragma: no cover - network-dependent path
            failures.append(f"{feed.id}: {exc}")
            continue

        total_seen += len(articles)
        for article in articles:
            upsert_article(db_path, article)
            total_stored += 1

        print(f"Fetched {len(articles)} article(s) from {feed.name}")

    print(f"RSS fetch complete: seen={total_seen}, stored_or_updated={total_stored}")
    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1 if total_seen == 0 else 0
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    db_path = Path(args.db)
    init_db(db_path)

    if args.date:
        report_date = args.date
    else:
        report_date = datetime.now().date().isoformat()

    articles = list_articles_for_date(db_path, report_date)
    scorer = TopicScorer()

    print(f"Newsroom report for {report_date}")
    print(f"Articles: {len(articles)}")
    if not articles:
        print("No article candidates stored for this date.")
        return 0

    for index, article in enumerate(articles, start=1):
        score = scorer.score_article(article)
        published = article.published_at or "unknown"
        print(f"{index}. [{score.score_total:.1f}] {article.title}")
        print(f"   source: {article.source_name} | published: {published}")
        print(f"   url: {article.url}")
        print(f"   score_components: {score.components}")

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "fetch":
        return cmd_fetch(args)
    if args.command == "report":
        return cmd_report(args)

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

