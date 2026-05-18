from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from datetime import datetime
from pathlib import Path

from newsroom.clustering.story_clusterer import StoryClusterer
from newsroom.config import DEFAULT_SERIES_CONFIG, load_series, load_source_feeds
from newsroom.ingest.inoreader_client import InoreaderClient
from newsroom.ingest.rss_client import RssClient
from newsroom.notebook.exporters import write_packet
from newsroom.notebook.packet_builder import DEFAULT_PACKET_ROOT, NotebookPacketBuilder
from newsroom.scoring.topic_scorer import TopicScorer
from newsroom.store.db import (
    DEFAULT_DB_PATH,
    init_db,
    list_articles_for_date,
    list_clusters_for_date,
    list_topic_scores_for_date,
    replace_clusters_for_date,
    upsert_article,
    upsert_topic_score,
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

    cluster_parser = subparsers.add_parser("cluster", help="Group daily articles into story clusters")
    _add_date_args(cluster_parser)
    cluster_parser.add_argument(
        "--threshold",
        type=float,
        default=0.4,
        help="Similarity threshold (0.0-1.0) for grouping articles",
    )

    score_parser = subparsers.add_parser("score", help="Score story clusters for a date")
    _add_date_args(score_parser)

    shortlist_parser = subparsers.add_parser("shortlist", help="Print the top scored story clusters")
    _add_date_args(shortlist_parser)
    shortlist_parser.add_argument("--top", type=int, default=10, help="Number of stories to print")

    packet_parser = subparsers.add_parser("packet", help="NotebookLM packet operations")
    packet_sub = packet_parser.add_subparsers(dest="packet_command", required=True)

    packet_build = packet_sub.add_parser("build", help="Build a packet from a story cluster")
    packet_build.add_argument("--story", required=True, help="Story cluster id")
    packet_build.add_argument(
        "--series-config",
        default=str(DEFAULT_SERIES_CONFIG),
        help="series.yml path used to resolve format_hint",
    )
    packet_build.add_argument(
        "--packet-root",
        default=str(DEFAULT_PACKET_ROOT),
        help="Root directory for packet artifact bundles",
    )
    packet_build.add_argument(
        "--format",
        dest="format_override",
        choices=["yukkuri", "anchor", "information_program"],
        help="Override the auto-resolved format_hint",
    )

    return parser


def _add_date_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--today", action="store_true", help="Use the local current date")
    group.add_argument("--date", help="Date in YYYY-MM-DD format")


def _resolve_date(args: argparse.Namespace) -> str:
    if getattr(args, "date", None):
        return args.date
    return datetime.now().date().isoformat()


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

    report_date = _resolve_date(args)

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


def cmd_cluster(args: argparse.Namespace) -> int:
    db_path = Path(args.db)
    init_db(db_path)
    cluster_date = _resolve_date(args)

    articles = list_articles_for_date(db_path, cluster_date)
    if not articles:
        print(f"No articles stored for {cluster_date}; nothing to cluster.")
        replace_clusters_for_date(db_path, cluster_date, [])
        return 0

    clusterer = StoryClusterer(threshold=args.threshold)
    clusters = clusterer.cluster(articles, cluster_date)
    replace_clusters_for_date(db_path, cluster_date, clusters)

    multi_member = [c for c in clusters if len(c.article_ids) > 1]
    print(f"Clustered {len(articles)} article(s) into {len(clusters)} story cluster(s) for {cluster_date}.")
    print(f"Multi-article clusters: {len(multi_member)}")
    for index, cluster in enumerate(multi_member, start=1):
        print(f"  {index}. {cluster.title}  ({len(cluster.article_ids)} articles, entities={cluster.entities})")
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    db_path = Path(args.db)
    init_db(db_path)
    cluster_date = _resolve_date(args)

    clusters = list_clusters_for_date(db_path, cluster_date)
    if not clusters:
        print(f"No clusters for {cluster_date}; run 'newsroom cluster' first.")
        return 0

    article_lookup = {article.id: article for article in list_articles_for_date(db_path, cluster_date)}
    scorer = TopicScorer()
    scored = 0
    for cluster in clusters:
        members = [article_lookup[article_id] for article_id in cluster.article_ids if article_id in article_lookup]
        if not members:
            continue
        score = scorer.score_cluster(cluster, members)
        upsert_topic_score(db_path, score)
        scored += 1

    print(f"Scored {scored} cluster(s) for {cluster_date}.")
    return 0


def cmd_shortlist(args: argparse.Namespace) -> int:
    db_path = Path(args.db)
    init_db(db_path)
    cluster_date = _resolve_date(args)

    scores = list_topic_scores_for_date(db_path, cluster_date)
    if not scores:
        print(f"No scored clusters for {cluster_date}; run 'newsroom cluster' then 'newsroom score'.")
        return 0

    clusters_by_id = {cluster.id: cluster for cluster in list_clusters_for_date(db_path, cluster_date)}

    top = scores[: max(args.top, 0)]
    print(f"Daily shortlist for {cluster_date} (top {len(top)} of {len(scores)}):")
    for index, score in enumerate(top, start=1):
        cluster = clusters_by_id.get(score.cluster_id)
        if cluster is None:
            continue
        print(f"{index}. [{score.score_total:.1f}] {cluster.title}")
        print(
            f"   articles={len(cluster.article_ids)}  sources={cluster.primary_sources}  "
            f"entities={cluster.entities}"
        )
        print(f"   components: {score.components}")
    return 0


def cmd_packet(args: argparse.Namespace) -> int:
    if args.packet_command != "build":
        print(f"Unsupported packet subcommand: {args.packet_command}")
        return 2

    db_path = Path(args.db)
    init_db(db_path)

    target_cluster = None
    target_date = None
    for date_dir_row in _iter_cluster_dates(db_path):
        clusters = list_clusters_for_date(db_path, date_dir_row)
        for cluster in clusters:
            if cluster.id == args.story:
                target_cluster = cluster
                target_date = date_dir_row
                break
        if target_cluster is not None:
            break

    if target_cluster is None:
        print(f"Story cluster not found: {args.story}")
        return 1

    articles = [
        article
        for article in list_articles_for_date(db_path, target_date)
        if article.id in target_cluster.article_ids
    ]
    if not articles:
        print(f"No articles resolvable for cluster {args.story}")
        return 1

    try:
        series_list = load_series(args.series_config)
        series_index = {series.id: series for series in series_list}
    except FileNotFoundError:
        series_index = {}

    builder = NotebookPacketBuilder(series_index=series_index)
    packet = builder.build(target_cluster, articles, packet_root=Path(args.packet_root))
    if args.format_override:
        packet = replace(packet, format_hint=args.format_override)

    output_dir = write_packet(packet)
    print(f"Packet built: {packet.id}")
    print(f"Export dir: {output_dir}")
    print(f"Format hint: {packet.format_hint}")
    print(f"Primary sources: {len(packet.primary_sources)}  News sources: {len(packet.news_sources)}")
    return 0


def _iter_cluster_dates(db_path: Path) -> list[str]:
    from newsroom.store.db import connect

    with connect(db_path) as connection:
        rows = connection.execute(
            "SELECT DISTINCT cluster_date FROM story_clusters ORDER BY cluster_date DESC"
        ).fetchall()
    return [row["cluster_date"] for row in rows]


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    dispatchers = {
        "fetch": cmd_fetch,
        "report": cmd_report,
        "cluster": cmd_cluster,
        "score": cmd_score,
        "shortlist": cmd_shortlist,
        "packet": cmd_packet,
    }
    handler = dispatchers.get(args.command)
    if handler is None:
        parser.error(f"Unknown command: {args.command}")
        return 2
    return handler(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
