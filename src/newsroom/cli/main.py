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
from newsroom.script.episode_planner import EpisodePlanner
from newsroom.script.exporters import DEFAULT_SCRIPT_ROOT, write_script_bundle
from newsroom.script.script_critic import ScriptCritic
from newsroom.script.script_drafter import ScriptDrafter
from newsroom.store.db import (
    DEFAULT_DB_PATH,
    init_db,
    list_articles_for_date,
    list_clusters_for_date,
    list_topic_scores_for_date,
    load_episode_plan,
    load_script_ir,
    replace_clusters_for_date,
    upsert_article,
    upsert_episode_plan,
    upsert_script_ir,
    upsert_topic_score,
)
from newsroom.store.models import ScriptIR, StoryCluster


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

    script_parser = subparsers.add_parser("script", help="Script workbench operations")
    script_sub = script_parser.add_subparsers(dest="script_command", required=True)

    script_draft = script_sub.add_parser("draft", help="Draft a script skeleton from a story cluster")
    script_draft.add_argument("--story", required=True, help="Story cluster id")
    script_draft.add_argument(
        "--format",
        required=True,
        choices=["yukkuri", "anchor"],
        help="Script format (yukkuri -> yukkuri_dialogue, anchor -> anchor_narration)",
    )
    script_draft.add_argument(
        "--series-config",
        default=str(DEFAULT_SERIES_CONFIG),
        help="series.yml path used to resolve series strategic_question",
    )
    script_draft.add_argument(
        "--script-root",
        default=str(DEFAULT_SCRIPT_ROOT),
        help="Root directory for script bundles",
    )

    script_critique = script_sub.add_parser("critique", help="Re-run editorial guards on a script")
    script_critique.add_argument("--script", required=True, help="Script id")
    script_critique.add_argument(
        "--script-root",
        default=str(DEFAULT_SCRIPT_ROOT),
        help="Root directory for script bundles",
    )

    script_revise = script_sub.add_parser("revise", help="Adjust script gear and rewrite bundle")
    script_revise.add_argument("--script", required=True, help="Script id")
    script_revise.add_argument("--gear", type=int, choices=[0, 1, 2, 3], required=True)
    script_revise.add_argument(
        "--script-root",
        default=str(DEFAULT_SCRIPT_ROOT),
        help="Root directory for script bundles",
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


def _iter_cluster_dates(db_path: Path) -> list[str]:
    from newsroom.store.db import connect

    with connect(db_path) as connection:
        rows = connection.execute(
            "SELECT DISTINCT cluster_date FROM story_clusters ORDER BY cluster_date DESC"
        ).fetchall()
    return [row["cluster_date"] for row in rows]


def _find_cluster(db_path: Path, cluster_id: str) -> tuple[StoryCluster, str] | None:
    for date in _iter_cluster_dates(db_path):
        for cluster in list_clusters_for_date(db_path, date):
            if cluster.id == cluster_id:
                return cluster, date
    return None


def _load_series_index(path: str) -> dict[str, object]:
    try:
        series_list = load_series(path)
    except FileNotFoundError:
        return {}
    return {series.id: series for series in series_list}


def cmd_packet(args: argparse.Namespace) -> int:
    if args.packet_command != "build":
        print(f"Unsupported packet subcommand: {args.packet_command}")
        return 2

    db_path = Path(args.db)
    init_db(db_path)

    found = _find_cluster(db_path, args.story)
    if found is None:
        print(f"Story cluster not found: {args.story}")
        return 1
    target_cluster, target_date = found

    articles = [
        article
        for article in list_articles_for_date(db_path, target_date)
        if article.id in target_cluster.article_ids
    ]
    if not articles:
        print(f"No articles resolvable for cluster {args.story}")
        return 1

    series_index = _load_series_index(args.series_config)
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


def _format_to_ir_name(short_name: str) -> str:
    return {"yukkuri": "yukkuri_dialogue", "anchor": "anchor_narration"}[short_name]


def _series_for_cluster(series_index: dict, cluster: StoryCluster):
    for series_tag in cluster.related_series:
        series_id = series_tag.split("/", 1)[1] if "/" in series_tag else series_tag
        series = series_index.get(series_id)
        if series is not None:
            return series
    return None


def _apply_gear(script: ScriptIR, gear: int) -> ScriptIR:
    if gear == 3:
        new_segments = [
            replace(segment, needs_human_review=(segment.claim_type == "fact"))
            for segment in script.segments
        ]
    else:
        new_segments = [replace(segment, needs_human_review=True) for segment in script.segments]
    return replace(script, segments=new_segments)


def cmd_script(args: argparse.Namespace) -> int:
    db_path = Path(args.db)
    init_db(db_path)

    if args.script_command == "draft":
        return _cmd_script_draft(args, db_path)
    if args.script_command == "critique":
        return _cmd_script_critique(args, db_path)
    if args.script_command == "revise":
        return _cmd_script_revise(args, db_path)
    print(f"Unsupported script subcommand: {args.script_command}")
    return 2


def _cmd_script_draft(args: argparse.Namespace, db_path: Path) -> int:
    found = _find_cluster(db_path, args.story)
    if found is None:
        print(f"Story cluster not found: {args.story}")
        return 1
    cluster, cluster_date = found

    articles = [
        article
        for article in list_articles_for_date(db_path, cluster_date)
        if article.id in cluster.article_ids
    ]
    if not articles:
        print(f"No articles resolvable for cluster {args.story}")
        return 1

    series_index = _load_series_index(args.series_config)
    packet_builder = NotebookPacketBuilder(series_index=series_index)
    packet = packet_builder.build(cluster, articles)

    series = _series_for_cluster(series_index, cluster)
    plan = EpisodePlanner().plan(cluster, packet, series=series)
    upsert_episode_plan(db_path, plan)

    ir_format = _format_to_ir_name(args.format)
    script = ScriptDrafter().draft(plan, packet, ir_format)
    upsert_script_ir(db_path, script)

    findings = ScriptCritic().critique(script, plan, packet)
    output_dir = write_script_bundle(plan, script, findings, script_root=Path(args.script_root))

    fail_count = sum(1 for f in findings if f.severity == "fail")
    warn_count = sum(1 for f in findings if f.severity == "warn")
    print(f"Script drafted: {script.id}")
    print(f"Episode plan: {plan.id}")
    print(f"Format: {script.format}  Segments: {len(script.segments)}")
    print(f"Output dir: {output_dir}")
    print(f"Critique: fail={fail_count}  warn={warn_count}  ok={len(findings) - fail_count - warn_count}")
    return 0


def _cmd_script_critique(args: argparse.Namespace, db_path: Path) -> int:
    script = load_script_ir(db_path, args.script)
    if script is None:
        print(f"Script not found: {args.script}")
        return 1
    plan = load_episode_plan(db_path, script.episode_plan_id)
    if plan is None:
        print(f"Episode plan not found for script {args.script}: {script.episode_plan_id}")
        return 1

    found = _find_cluster(db_path, plan.story_cluster_id)
    if found is None:
        print(f"Cluster not found for plan {plan.id}: {plan.story_cluster_id}")
        return 1
    cluster, cluster_date = found
    articles = [
        article
        for article in list_articles_for_date(db_path, cluster_date)
        if article.id in cluster.article_ids
    ]
    series_index = _load_series_index(str(DEFAULT_SERIES_CONFIG))
    packet = NotebookPacketBuilder(series_index=series_index).build(cluster, articles)

    findings = ScriptCritic().critique(script, plan, packet)
    output_dir = write_script_bundle(plan, script, findings, script_root=Path(args.script_root))

    print(f"Critique refreshed for {script.id}")
    for finding in findings:
        print(f"  [{finding.severity}] {finding.guard}: {finding.message}")
    print(f"Output dir: {output_dir}")
    return 0


def _cmd_script_revise(args: argparse.Namespace, db_path: Path) -> int:
    script = load_script_ir(db_path, args.script)
    if script is None:
        print(f"Script not found: {args.script}")
        return 1
    plan = load_episode_plan(db_path, script.episode_plan_id)
    if plan is None:
        print(f"Episode plan not found for script {args.script}: {script.episode_plan_id}")
        return 1

    updated = _apply_gear(script, args.gear)
    upsert_script_ir(db_path, updated)

    found = _find_cluster(db_path, plan.story_cluster_id)
    if found is None:
        print(f"Cluster not found for plan {plan.id}: {plan.story_cluster_id}")
        return 1
    cluster, cluster_date = found
    articles = [
        article
        for article in list_articles_for_date(db_path, cluster_date)
        if article.id in cluster.article_ids
    ]
    series_index = _load_series_index(str(DEFAULT_SERIES_CONFIG))
    packet = NotebookPacketBuilder(series_index=series_index).build(cluster, articles)
    findings = ScriptCritic().critique(updated, plan, packet)
    output_dir = write_script_bundle(plan, updated, findings, script_root=Path(args.script_root))

    print(f"Script revised to gear {args.gear}: {updated.id}")
    print(f"Output dir: {output_dir}")
    review_segments = sum(1 for seg in updated.segments if seg.needs_human_review)
    print(f"Segments flagged for human review: {review_segments} / {len(updated.segments)}")
    return 0


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
        "script": cmd_script,
    }
    handler = dispatchers.get(args.command)
    if handler is None:
        parser.error(f"Unknown command: {args.command}")
        return 2
    return handler(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
