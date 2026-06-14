from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from newsroom.clustering.story_clusterer import StoryClusterer
from newsroom.config import DEFAULT_SERIES_CONFIG, load_series, load_source_feeds
from newsroom.editorial.channel_memory import (
    DEFAULT_CHANNEL_MEMORY_ROOT,
    ChannelMemoryValidationError,
    append_episode_record,
    load_channel_memory,
    render_channel_memory_report,
)
from newsroom.ingest.inoreader_client import InoreaderClient
from newsroom.ingest.rss_client import RssClient
from newsroom.adapters.ymm4_export import (
    DEFAULT_EXPORT_ROOT,
    build_ymm4_package,
    export_episode_id,
)
from newsroom.adapters.export_inspector import inspect_episode_bundle
from newsroom.assets.asset_registry import AssetRegistry
from newsroom.assets.exporters import (
    DEFAULT_ASSET_ROOT,
    DEFAULT_QUOTE_ROOT,
    load_asset_manifest,
    load_quote_manifest,
    write_asset_manifest,
    write_quote_manifest,
)
from newsroom.assets.quote_manifest import QuoteManifestBuilder
from newsroom.layout.exporters import DEFAULT_VISUAL_ROOT, write_visual_bundle
from newsroom.layout.visual_planner import VisualPlanner
from newsroom.notebook.exporters import write_packet
from newsroom.notebook.packet_builder import DEFAULT_PACKET_ROOT, NotebookPacketBuilder
from newsroom.scoring.topic_scorer import TopicScorer
from newsroom.script.episode_planner import EpisodePlanner
from newsroom.script.exporters import DEFAULT_SCRIPT_ROOT, write_script_bundle
from newsroom.script.materialization import (
    APPROVED_MATERIALIZATION_DEFAULT_ROOT,
    MaterializationValidationError,
    apply_approved_materialization_record,
    apply_materialization_draft,
    write_approved_materialization_record,
    write_materialization_draft,
)
from newsroom.script.script_critic import ScriptCritic
from newsroom.script.script_drafter import ScriptDrafter
from newsroom.store.db import (
    DEFAULT_DB_PATH,
    add_story_critical_source,
    init_db,
    list_articles_by_ids,
    list_articles_for_date,
    list_articles_in_date_range,
    list_clusters_for_date,
    list_story_critical_sources,
    list_story_critical_source_articles,
    list_topic_scores_for_date,
    load_episode_plan,
    load_notebook_packet,
    load_notebook_packet_for_story,
    load_script_ir,
    load_visual_ir,
    load_visual_ir_for_script,
    replace_clusters_for_date,
    upsert_article,
    upsert_episode_plan,
    upsert_notebook_packet,
    upsert_script_ir,
    upsert_topic_score,
    upsert_visual_ir,
)
from newsroom.store.models import Article, NotebookPacket, ScriptIR, StoryCluster


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

    cluster_parser = subparsers.add_parser("cluster", help="Group articles into story clusters")
    _add_cluster_window_args(cluster_parser)
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

    series_parser = subparsers.add_parser("series", help="Series memory operations")
    series_sub = series_parser.add_subparsers(dest="series_command", required=True)
    series_report = series_sub.add_parser(
        "report",
        help="Read back a tracked channel memory report",
    )
    series_report.add_argument("--series", required=True, help="Series id, e.g. copilot_watch")
    series_report.add_argument(
        "--memory-root",
        default=str(DEFAULT_CHANNEL_MEMORY_ROOT),
        help="Root directory for tracked channel memory YAML records",
    )
    series_append = series_sub.add_parser(
        "append-episode",
        help="Append an approved episode record to tracked channel memory",
    )
    series_append.add_argument("--series", required=True, help="Series id, e.g. copilot_watch")
    series_append.add_argument(
        "--episode-record",
        required=True,
        help="YAML episode record to append after validation",
    )
    series_append.add_argument(
        "--memory-root",
        default=str(DEFAULT_CHANNEL_MEMORY_ROOT),
        help="Root directory for tracked channel memory YAML records",
    )

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
    packet_show = packet_sub.add_parser(
        "show",
        help="Read back a persisted NotebookPacket from the runtime DB",
    )
    packet_show_target = packet_show.add_mutually_exclusive_group(required=True)
    packet_show_target.add_argument("--packet", dest="packet_id", help="NotebookPacket id")
    packet_show_target.add_argument("--story", dest="story_id", help="Story cluster id")
    packet_critical = packet_sub.add_parser(
        "add-critical",
        help="Record a critical-view source for a story packet",
    )
    packet_critical.add_argument("--story", required=True, help="Story cluster id")
    critical_source = packet_critical.add_mutually_exclusive_group(required=True)
    critical_source.add_argument("--article", dest="article_id", help="Existing article id")
    critical_source.add_argument("--url", help="Manual source URL")
    packet_critical.add_argument("--title", help="Manual source title; required with --url")
    packet_critical.add_argument("--source-name", help="Manual source name; required with --url")
    packet_critical.add_argument(
        "--source-type",
        choices=["official", "news", "commentary", "competitor", "social", "unknown"],
        default="commentary",
        help="Manual source type used when --url is supplied",
    )
    packet_critical.add_argument("--published-at", help="Manual source published timestamp")
    packet_critical.add_argument("--license-hint", help="Manual source license hint")
    packet_critical.add_argument("--note", help="Operator note explaining the critical angle")
    packet_list_critical = packet_sub.add_parser(
        "list-critical",
        help="Read back critical-view sources recorded for a story",
    )
    packet_list_critical.add_argument("--story", required=True, help="Story cluster id")

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

    script_materialize = script_sub.add_parser(
        "materialize",
        help="Write an operator-editable script materialization draft",
    )
    script_materialize.add_argument("--script", required=True, help="Script id")
    script_materialize.add_argument(
        "--script-root",
        default=str(DEFAULT_SCRIPT_ROOT),
        help="Root directory for script materialization draft bundles",
    )
    script_materialize.add_argument(
        "--series-config",
        default=str(DEFAULT_SERIES_CONFIG),
        help="series.yml path used when rebuilding the packet",
    )

    script_apply_materialization = script_sub.add_parser(
        "apply-materialization",
        help="Apply an operator-approved script materialization draft",
    )
    script_apply_materialization.add_argument("--script", required=True, help="Script id")
    script_apply_materialization.add_argument(
        "--draft",
        required=True,
        help="Path to script_materialization.yml with approved operator_fill values",
    )
    script_apply_materialization.add_argument(
        "--require-approved",
        action="store_true",
        default=True,
        help="Require replacement_status=approved for each replaced TODO segment",
    )
    script_apply_materialization.add_argument(
        "--script-root",
        default=str(DEFAULT_SCRIPT_ROOT),
        help="Root directory for refreshed script bundles",
    )
    script_apply_materialization.add_argument(
        "--series-config",
        default=str(DEFAULT_SERIES_CONFIG),
        help="series.yml path used when rebuilding the packet",
    )

    script_approve_materialization = script_sub.add_parser(
        "approve-materialization",
        help="Write a tracked sanitized approved materialization record",
    )
    script_approve_materialization.add_argument("--script", required=True, help="Script id")
    script_approve_materialization.add_argument(
        "--draft",
        required=True,
        help="Path to script_materialization.yml with approved operator_fill values",
    )
    script_approve_materialization.add_argument(
        "--output-root",
        default=str(APPROVED_MATERIALIZATION_DEFAULT_ROOT),
        help="Root directory for tracked approved materialization records",
    )
    script_approve_materialization.add_argument(
        "--episode-id",
        help="Optional episode id the approved record is intended to rebuild",
    )
    script_approve_materialization.add_argument(
        "--approved-by",
        required=True,
        help="Operator or reviewer who approved the narration",
    )
    script_approve_materialization.add_argument(
        "--approved-at",
        help="Approval timestamp; defaults to current UTC time",
    )
    script_approve_materialization.add_argument(
        "--approval-note",
        help="Short approval note; do not include raw article body or private data",
    )
    script_approve_materialization.add_argument(
        "--require-approved",
        action="store_true",
        default=True,
        help="Require replacement_status=approved for each replaced TODO segment",
    )

    script_apply_approved_materialization = script_sub.add_parser(
        "apply-approved-materialization",
        help="Apply a tracked approved materialization record",
    )
    script_apply_approved_materialization.add_argument("--script", required=True, help="Script id")
    script_apply_approved_materialization.add_argument(
        "--record",
        required=True,
        help="Path to docs/approved_materializations/<script_id>.materialization.yml",
    )
    script_apply_approved_materialization.add_argument(
        "--script-root",
        default=str(DEFAULT_SCRIPT_ROOT),
        help="Root directory for refreshed script bundles",
    )
    script_apply_approved_materialization.add_argument(
        "--series-config",
        default=str(DEFAULT_SERIES_CONFIG),
        help="series.yml path used when rebuilding the packet",
    )

    asset_parser = subparsers.add_parser("asset", help="Asset manifest operations")
    asset_sub = asset_parser.add_subparsers(dest="asset_command", required=True)

    asset_suggest = asset_sub.add_parser("suggest", help="Suggest asset candidates from a script's VisualIR")
    asset_suggest.add_argument("--script", required=True, help="Script id")
    asset_suggest.add_argument(
        "--asset-root",
        default=str(DEFAULT_ASSET_ROOT),
        help="Root directory for asset manifests",
    )
    asset_suggest.add_argument(
        "--series-config",
        default=str(DEFAULT_SERIES_CONFIG),
        help="series.yml path used when rebuilding the packet",
    )

    quote_parser = subparsers.add_parser("quote", help="Quote manifest operations")
    quote_sub = quote_parser.add_subparsers(dest="quote_command", required=True)

    quote_suggest = quote_sub.add_parser(
        "suggest",
        help="Suggest quote review rows from a script",
    )
    quote_suggest.add_argument("--script", required=True, help="Script id")
    quote_suggest.add_argument(
        "--quote-root",
        default=str(DEFAULT_QUOTE_ROOT),
        help="Root directory for quote manifests",
    )
    quote_suggest.add_argument(
        "--series-config",
        default=str(DEFAULT_SERIES_CONFIG),
        help="series.yml path used when rebuilding the packet",
    )

    visual_parser = subparsers.add_parser("visual", help="Visual planning operations")
    visual_sub = visual_parser.add_subparsers(dest="visual_command", required=True)

    visual_plan = visual_sub.add_parser("plan", help="Plan VisualIR for a script")
    visual_plan.add_argument("--script", required=True, help="Script id")
    visual_plan.add_argument(
        "--visual-root",
        default=str(DEFAULT_VISUAL_ROOT),
        help="Root directory for visual bundles",
    )
    visual_plan.add_argument(
        "--series-config",
        default=str(DEFAULT_SERIES_CONFIG),
        help="series.yml path used when rebuilding the packet",
    )

    export_parser = subparsers.add_parser("export", help="Export packages for downstream tools")
    export_sub = export_parser.add_subparsers(dest="export_command", required=True)

    export_inspect = export_sub.add_parser(
        "inspect",
        help="Inspect an episode export bundle before manual YMM4 import",
    )
    export_inspect.add_argument("--episode-dir", required=True, help="Episode export directory")

    export_ymm4 = export_sub.add_parser("ymm4", help="Build the YMM4 export bundle for a script")
    export_ymm4.add_argument("--script", required=True, help="Script id")
    export_ymm4.add_argument(
        "--export-root",
        default=str(DEFAULT_EXPORT_ROOT),
        help="Root directory for episode export bundles",
    )
    export_ymm4.add_argument(
        "--series-config",
        default=str(DEFAULT_SERIES_CONFIG),
        help="series.yml path used when rebuilding the packet",
    )
    export_ymm4.add_argument(
        "--asset-root",
        default=str(DEFAULT_ASSET_ROOT),
        help="Root directory used to reuse existing asset manifests",
    )
    export_ymm4.add_argument(
        "--quote-root",
        default=str(DEFAULT_QUOTE_ROOT),
        help="Root directory used to reuse existing quote manifests",
    )

    return parser


def _add_date_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--today", action="store_true", help="Use the local current date")
    group.add_argument("--date", help="Date in YYYY-MM-DD format")


def _add_cluster_window_args(parser: argparse.ArgumentParser) -> None:
    """Cluster CLI accepts a single date OR a multi-day window.

    --today / --date / --days are mutually exclusive single-anchor flags.
    --from and --to must be paired and cannot mix with the single-anchor
    flags. The resulting cluster_date is always the end of the window so
    score / shortlist can keep using their existing --date semantics.
    """
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--today", action="store_true", help="Use the local current date")
    group.add_argument("--date", help="Single date YYYY-MM-DD")
    group.add_argument(
        "--days",
        type=int,
        help="Number of days back from today (inclusive); end of window is today",
    )
    parser.add_argument(
        "--from",
        dest="date_from",
        help="Range start YYYY-MM-DD (must be paired with --to)",
    )
    parser.add_argument(
        "--to",
        dest="date_to",
        help="Range end YYYY-MM-DD (must be paired with --from)",
    )


def _resolve_date(args: argparse.Namespace) -> str:
    if getattr(args, "date", None):
        return args.date
    return datetime.now().date().isoformat()


def _resolve_date_range(args: argparse.Namespace) -> tuple[str, str]:
    """Return (start_date, end_date) inclusive based on cluster window flags."""
    date_from = getattr(args, "date_from", None)
    date_to = getattr(args, "date_to", None)
    days = getattr(args, "days", None)
    single_date = getattr(args, "date", None)
    today_flag = bool(getattr(args, "today", False))

    range_specified = bool(date_from) or bool(date_to)
    anchor_specified = bool(days) or bool(single_date) or today_flag

    if range_specified and anchor_specified:
        raise SystemExit("--from/--to cannot be combined with --today / --date / --days")
    if bool(date_from) != bool(date_to):
        raise SystemExit("--from and --to must be specified together")

    if date_from and date_to:
        if date_from > date_to:
            raise SystemExit("--from must be on or before --to")
        return date_from, date_to

    if days:
        if days < 1:
            raise SystemExit("--days must be >= 1")
        end = date.today()
        start = end - timedelta(days=days - 1)
        return start.isoformat(), end.isoformat()

    if single_date:
        return single_date, single_date

    today = date.today().isoformat()
    return today, today


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

    start_date, end_date = _resolve_date_range(args)
    cluster_date = end_date

    if start_date == end_date:
        articles = list_articles_for_date(db_path, start_date)
        window_label = start_date
    else:
        articles = list_articles_in_date_range(db_path, start_date, end_date)
        window_label = f"{start_date}..{end_date}"

    if not articles:
        print(f"No articles in window {window_label}; nothing to cluster.")
        replace_clusters_for_date(db_path, cluster_date, [])
        return 0

    clusterer = StoryClusterer(threshold=args.threshold)
    clusters = clusterer.cluster(articles, cluster_date)
    replace_clusters_for_date(db_path, cluster_date, clusters)

    multi_member = [c for c in clusters if len(c.article_ids) > 1]
    print(
        f"Clustered {len(articles)} article(s) over {window_label} into "
        f"{len(clusters)} story cluster(s)."
    )
    if start_date != end_date:
        print(f"Cluster date (for score/shortlist): {cluster_date}")
    print(f"Multi-article clusters: {len(multi_member)}")
    for index, cluster in enumerate(multi_member, start=1):
        print(
            f"  {index}. {cluster.title}  "
            f"({len(cluster.article_ids)} articles, entities={cluster.entities})"
        )
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    db_path = Path(args.db)
    init_db(db_path)
    cluster_date = _resolve_date(args)

    clusters = list_clusters_for_date(db_path, cluster_date)
    if not clusters:
        print(f"No clusters for {cluster_date}; run 'newsroom cluster' first.")
        return 0

    all_ids = sorted({aid for cluster in clusters for aid in cluster.article_ids})
    article_lookup = {article.id: article for article in list_articles_by_ids(db_path, all_ids)}

    scorer = TopicScorer()
    scored = 0
    for cluster in clusters:
        members = [article_lookup[aid] for aid in cluster.article_ids if aid in article_lookup]
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


def _force_utf8_stdio() -> None:
    """Reconfigure stdout/stderr to UTF-8 so the CLI never crashes on em-dash
    or Japanese characters when run from a Windows console (cp932 default).

    The artifact files are already written in UTF-8; only the console print
    path is affected by the legacy codec.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            continue


def _iter_cluster_dates(db_path: Path) -> list[str]:
    from newsroom.store.db import connect

    with connect(db_path) as connection:
        rows = connection.execute(
            "SELECT DISTINCT cluster_date FROM story_clusters ORDER BY cluster_date DESC"
        ).fetchall()
    return [row["cluster_date"] for row in rows]


def _find_cluster(db_path: Path, cluster_id: str) -> tuple[StoryCluster, str] | None:
    for cluster_date_value in _iter_cluster_dates(db_path):
        for cluster in list_clusters_for_date(db_path, cluster_date_value):
            if cluster.id == cluster_id:
                return cluster, cluster_date_value
    return None


def _articles_for_cluster(db_path: Path, cluster: StoryCluster):
    return list_articles_by_ids(db_path, cluster.article_ids)


def _load_series_index(path: str) -> dict[str, object]:
    try:
        series_list = load_series(path)
    except FileNotFoundError:
        return {}
    return {series.id: series for series in series_list}


def cmd_series(args: argparse.Namespace) -> int:
    if args.series_command == "report":
        return _cmd_series_report(args)
    if args.series_command == "append-episode":
        return _cmd_series_append_episode(args)
    print(f"Unsupported series subcommand: {args.series_command}")
    return 2


def _cmd_series_report(args: argparse.Namespace) -> int:
    memory_path = Path(args.memory_root) / f"{args.series}.yml"
    if not memory_path.exists():
        print(f"Channel memory not found: {memory_path}")
        return 1
    memory = load_channel_memory(memory_path)
    print(render_channel_memory_report(memory))
    return 0


def _cmd_series_append_episode(args: argparse.Namespace) -> int:
    memory_path = Path(args.memory_root) / f"{args.series}.yml"
    if not memory_path.exists():
        print(f"Channel memory not found: {memory_path}")
        return 1
    try:
        memory = append_episode_record(memory_path, args.episode_record)
    except (ChannelMemoryValidationError, FileNotFoundError) as exc:
        print(f"Channel memory append failed: {exc}")
        return 1
    print(f"Appended episode record to {memory_path}")
    print(f"Series: {memory.title} ({memory.series_id})")
    print(f"Episodes: {len(memory.episodes)}")
    print("Important: follow-up seeds remain seeds and are not approved stories.")
    return 0


def cmd_packet(args: argparse.Namespace) -> int:
    db_path = Path(args.db)
    init_db(db_path)

    if args.packet_command == "build":
        return _cmd_packet_build(args, db_path)
    if args.packet_command == "show":
        return _cmd_packet_show(args, db_path)
    if args.packet_command == "add-critical":
        return _cmd_packet_add_critical(args, db_path)
    if args.packet_command == "list-critical":
        return _cmd_packet_list_critical(args, db_path)
    print(f"Unsupported packet subcommand: {args.packet_command}")
    return 2


def _cmd_packet_build(args: argparse.Namespace, db_path: Path) -> int:
    found = _find_cluster(db_path, args.story)
    if found is None:
        print(f"Story cluster not found: {args.story}")
        return 1
    target_cluster, _ = found

    articles = _articles_for_cluster(db_path, target_cluster)
    if not articles:
        print(f"No articles resolvable for cluster {args.story}")
        return 1

    packet = _build_packet_for_cluster(
        db_path,
        target_cluster,
        articles,
        args.series_config,
        packet_root=Path(args.packet_root),
        prefer_persisted=False,
    )
    if args.format_override:
        packet = replace(packet, format_hint=args.format_override)

    upsert_notebook_packet(db_path, packet)
    output_dir = write_packet(packet)
    print(f"Packet built: {packet.id}")
    print(f"Export dir: {output_dir}")
    print(f"Format hint: {packet.format_hint}")
    print(
        f"Primary sources: {len(packet.primary_sources)}  "
        f"News sources: {len(packet.news_sources)}  "
        f"Critical views: {len(packet.critical_views)}"
    )
    return 0


def _cmd_packet_show(args: argparse.Namespace, db_path: Path) -> int:
    if args.packet_id:
        packet = load_notebook_packet(db_path, args.packet_id)
    else:
        packet = load_notebook_packet_for_story(db_path, args.story_id)
    if packet is None:
        target = args.packet_id or args.story_id
        print(f"NotebookPacket not found: {target}")
        return 1

    print(f"Packet: {packet.id}")
    print(f"Story: {packet.story_cluster_id}")
    print(f"Format hint: {packet.format_hint}")
    print(f"Export dir: {packet.export_dir}")
    print(
        f"Primary sources: {len(packet.primary_sources)}  "
        f"News sources: {len(packet.news_sources)}  "
        f"Critical views: {len(packet.critical_views)}"
    )
    print(f"Questions: {len(packet.questions)}  Glossary terms: {len(packet.glossary)}")
    return 0


def _cmd_packet_add_critical(args: argparse.Namespace, db_path: Path) -> int:
    found = _find_cluster(db_path, args.story)
    if found is None:
        print(f"Story cluster not found: {args.story}")
        return 1
    cluster, _ = found

    if args.article_id:
        matches = list_articles_by_ids(db_path, [args.article_id])
        if not matches:
            print(f"Article not found: {args.article_id}")
            return 1
        article = matches[0]
    else:
        if not args.title or not args.source_name:
            print("--title and --source-name are required when adding a manual --url source")
            return 2
        article = Article.create(
            url=args.url,
            title=args.title,
            source_name=args.source_name,
            source_type=args.source_type,
            published_at=args.published_at,
            fetched_at=datetime.now(UTC).isoformat(),
            tags=["manual", "critical_view"],
            license_hint=args.license_hint,
        )
        upsert_article(db_path, article)

    add_story_critical_source(
        db_path,
        cluster_id=cluster.id,
        article_id=article.id,
        note=args.note,
    )
    print(f"Critical-view source recorded for {cluster.id}: {article.id}")
    print(f"Title: {article.title}")
    print("Rebuild the packet to carry this source into downstream artifacts.")
    return 0


def _cmd_packet_list_critical(args: argparse.Namespace, db_path: Path) -> int:
    found = _find_cluster(db_path, args.story)
    if found is None:
        print(f"Story cluster not found: {args.story}")
        return 1
    cluster, _ = found

    records = list_story_critical_sources(db_path, cluster.id)
    print(f"Critical-view sources for {cluster.id}: {len(records)}")
    if not records:
        print("No critical-view sources recorded. Use packet add-critical before rebuilding the packet.")
        return 0

    for index, record in enumerate(records, start=1):
        article = record.article
        source_role = article.source_role or "unclassified"
        source_pool = article.source_pool_id or "no_pool"
        note = record.note or "none"
        print(
            f"{index}. {article.id} | {article.source_name} | "
            f"{article.source_type} / {source_role} / {source_pool}"
        )
        print(f"   title: {article.title}")
        print(f"   note: {note}")
        print(f"   recorded_at: {record.created_at}")
    print("This is readback only; rebuild the packet to carry sources into downstream artifacts.")
    return 0


def _build_packet_for_cluster(
    db_path: Path,
    cluster: StoryCluster,
    articles: list[Article],
    series_config: str,
    packet_root: Path | str = DEFAULT_PACKET_ROOT,
    prefer_persisted: bool = True,
) -> NotebookPacket:
    series_index = _load_series_index(series_config)
    critical_articles = list_story_critical_source_articles(db_path, cluster.id)
    fresh_packet = NotebookPacketBuilder(series_index=series_index).build(
        cluster,
        articles,
        packet_root=packet_root,
        critical_articles=critical_articles,
    )
    if not prefer_persisted:
        return fresh_packet
    persisted = load_notebook_packet_for_story(db_path, cluster.id)
    if persisted is None:
        upsert_notebook_packet(db_path, fresh_packet)
        return fresh_packet
    merged = _merge_required_packet_sources(persisted, fresh_packet)
    if merged != persisted:
        upsert_notebook_packet(db_path, merged)
    return merged


def _merge_required_packet_sources(
    persisted: NotebookPacket,
    fresh_packet: NotebookPacket,
) -> NotebookPacket:
    critical_by_id = {ref.article_id: ref for ref in persisted.critical_views}
    merged_critical = list(persisted.critical_views)
    for ref in fresh_packet.critical_views:
        if ref.article_id in critical_by_id:
            continue
        merged_critical.append(ref)
    if len(merged_critical) == len(persisted.critical_views):
        return persisted
    return replace(persisted, critical_views=merged_critical)


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
    if args.script_command == "materialize":
        return _cmd_script_materialize(args, db_path)
    if args.script_command == "apply-materialization":
        return _cmd_script_apply_materialization(args, db_path)
    if args.script_command == "approve-materialization":
        return _cmd_script_approve_materialization(args, db_path)
    if args.script_command == "apply-approved-materialization":
        return _cmd_script_apply_approved_materialization(args, db_path)
    print(f"Unsupported script subcommand: {args.script_command}")
    return 2


def _cmd_script_draft(args: argparse.Namespace, db_path: Path) -> int:
    found = _find_cluster(db_path, args.story)
    if found is None:
        print(f"Story cluster not found: {args.story}")
        return 1
    cluster, _ = found

    articles = _articles_for_cluster(db_path, cluster)
    if not articles:
        print(f"No articles resolvable for cluster {args.story}")
        return 1

    series_index = _load_series_index(args.series_config)
    packet = _build_packet_for_cluster(db_path, cluster, articles, args.series_config)

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
    cluster, _ = found
    articles = _articles_for_cluster(db_path, cluster)
    packet = _build_packet_for_cluster(
        db_path,
        cluster,
        articles,
        str(DEFAULT_SERIES_CONFIG),
    )

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
    cluster, _ = found
    articles = _articles_for_cluster(db_path, cluster)
    packet = _build_packet_for_cluster(
        db_path,
        cluster,
        articles,
        str(DEFAULT_SERIES_CONFIG),
    )
    findings = ScriptCritic().critique(updated, plan, packet)
    output_dir = write_script_bundle(plan, updated, findings, script_root=Path(args.script_root))

    print(f"Script revised to gear {args.gear}: {updated.id}")
    print(f"Output dir: {output_dir}")
    review_segments = sum(1 for seg in updated.segments if seg.needs_human_review)
    print(f"Segments flagged for human review: {review_segments} / {len(updated.segments)}")
    return 0


def _cmd_script_materialize(args: argparse.Namespace, db_path: Path) -> int:
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
    cluster, _ = found
    articles = _articles_for_cluster(db_path, cluster)
    if not articles:
        print(f"No articles resolvable for cluster {cluster.id}")
        return 1

    packet = _build_packet_for_cluster(db_path, cluster, articles, args.series_config)
    output_path = write_materialization_draft(
        plan,
        script,
        packet,
        script_root=Path(args.script_root),
    )

    todo_count = sum(1 for segment in script.segments if segment.text.startswith("TODO["))
    critical_ids = {ref.article_id for ref in packet.critical_views}
    critical_ref_count = sum(
        1
        for segment in script.segments
        if any(ref in critical_ids for ref in segment.source_refs)
    )
    print(f"Script materialization draft written: {output_path}")
    print(f"Script: {script.id}  TODO segments: {todo_count} / {len(script.segments)}")
    print(f"Segments carrying critical_refs: {critical_ref_count}")
    print("No script text was replaced; export inspect TODO warnings remain until operator-approved replacement.")
    return 0


def _cmd_script_apply_materialization(args: argparse.Namespace, db_path: Path) -> int:
    script = load_script_ir(db_path, args.script)
    if script is None:
        print(f"Script not found: {args.script}")
        return 1
    plan = load_episode_plan(db_path, script.episode_plan_id)
    if plan is None:
        print(f"Episode plan not found for script {args.script}: {script.episode_plan_id}")
        return 1

    try:
        updated = apply_materialization_draft(
            script,
            args.draft,
            require_approved=args.require_approved,
        )
    except MaterializationValidationError as exc:
        print(f"Script materialization rejected: {exc}")
        return 1

    found = _find_cluster(db_path, plan.story_cluster_id)
    if found is None:
        print(f"Cluster not found for plan {plan.id}: {plan.story_cluster_id}")
        return 1
    cluster, _ = found
    articles = _articles_for_cluster(db_path, cluster)
    if not articles:
        print(f"No articles resolvable for cluster {cluster.id}")
        return 1

    packet = _build_packet_for_cluster(db_path, cluster, articles, args.series_config)
    upsert_script_ir(db_path, updated)
    findings = ScriptCritic().critique(updated, plan, packet)
    output_dir = write_script_bundle(
        plan,
        updated,
        findings,
        script_root=Path(args.script_root),
    )

    replaced = sum(
        1
        for before, after in zip(script.segments, updated.segments, strict=True)
        if before.text != after.text
    )
    todo_remaining = sum(1 for segment in updated.segments if segment.text.startswith("TODO["))
    print(f"Script materialization applied: {updated.id}")
    print(f"Segments replaced: {replaced}  TODO remaining: {todo_remaining}")
    print(f"Output dir: {output_dir}")
    print("Export bundles were not rebuilt; rerun export after reviewing the refreshed script bundle.")
    return 0


def _cmd_script_approve_materialization(args: argparse.Namespace, db_path: Path) -> int:
    script = load_script_ir(db_path, args.script)
    if script is None:
        print(f"Script not found: {args.script}")
        return 1
    plan = load_episode_plan(db_path, script.episode_plan_id)
    if plan is None:
        print(f"Episode plan not found for script {args.script}: {script.episode_plan_id}")
        return 1

    try:
        output_path = write_approved_materialization_record(
            script,
            args.draft,
            story_cluster_id=plan.story_cluster_id,
            episode_id=args.episode_id,
            approved_by=args.approved_by,
            approved_at=args.approved_at,
            approval_note=args.approval_note,
            output_root=Path(args.output_root),
            require_approved=args.require_approved,
        )
    except MaterializationValidationError as exc:
        print(f"Approved materialization rejected: {exc}")
        return 1

    print(f"Approved materialization record written: {output_path}")
    print("Record is sanitized: no source_catalog, raw article body, runtime DB path, screenshots, or YMM4 geometry.")
    print("No ScriptIR or export bundle was modified; apply the approved record in a separate step.")
    return 0


def _cmd_script_apply_approved_materialization(args: argparse.Namespace, db_path: Path) -> int:
    script = load_script_ir(db_path, args.script)
    if script is None:
        print(f"Script not found: {args.script}")
        return 1
    plan = load_episode_plan(db_path, script.episode_plan_id)
    if plan is None:
        print(f"Episode plan not found for script {args.script}: {script.episode_plan_id}")
        return 1

    try:
        updated = apply_approved_materialization_record(script, args.record)
    except MaterializationValidationError as exc:
        print(f"Approved materialization rejected: {exc}")
        return 1

    found = _find_cluster(db_path, plan.story_cluster_id)
    if found is None:
        print(f"Cluster not found for plan {plan.id}: {plan.story_cluster_id}")
        return 1
    cluster, _ = found
    articles = _articles_for_cluster(db_path, cluster)
    if not articles:
        print(f"No articles resolvable for cluster {cluster.id}")
        return 1

    packet = _build_packet_for_cluster(db_path, cluster, articles, args.series_config)
    upsert_script_ir(db_path, updated)
    findings = ScriptCritic().critique(updated, plan, packet)
    output_dir = write_script_bundle(
        plan,
        updated,
        findings,
        script_root=Path(args.script_root),
    )

    replaced = sum(
        1
        for before, after in zip(script.segments, updated.segments, strict=True)
        if before.text != after.text
    )
    todo_remaining = sum(1 for segment in updated.segments if segment.text.startswith("TODO["))
    print(f"Approved materialization applied: {updated.id}")
    print(f"Segments replaced: {replaced}  TODO remaining: {todo_remaining}")
    print(f"Output dir: {output_dir}")
    print("Export bundles were not rebuilt; rerun export after reviewing the refreshed script bundle.")
    return 0


def cmd_asset(args: argparse.Namespace) -> int:
    if args.asset_command != "suggest":
        print(f"Unsupported asset subcommand: {args.asset_command}")
        return 2

    db_path = Path(args.db)
    init_db(db_path)

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
    cluster, _ = found
    articles = _articles_for_cluster(db_path, cluster)
    if not articles:
        print(f"No articles resolvable for cluster {cluster.id}")
        return 1

    packet = _build_packet_for_cluster(db_path, cluster, articles, args.series_config)

    visual_ir = load_visual_ir_for_script(db_path, script.id)
    if visual_ir is None:
        visual_ir = VisualPlanner().plan(script, plan, packet)
        upsert_visual_ir(db_path, visual_ir)

    manifest = AssetRegistry().suggest(visual_ir, packet, episode_id=plan.id)
    output_dir = write_asset_manifest(manifest, asset_root=Path(args.asset_root))

    human_required = sum(1 for a in manifest.assets if a.approval_state == "human_required")
    suggested = sum(1 for a in manifest.assets if a.approval_state == "suggested")
    print(f"Asset manifest written: {manifest.episode_id}")
    print(f"Script: {script.id}  VisualIR: {visual_ir.id}")
    print(f"Candidates: {len(manifest.assets)}  human_required: {human_required}  suggested: {suggested}")
    print(f"Output dir: {output_dir}")
    return 0


def cmd_quote(args: argparse.Namespace) -> int:
    if args.quote_command != "suggest":
        print(f"Unsupported quote subcommand: {args.quote_command}")
        return 2

    db_path = Path(args.db)
    init_db(db_path)

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
    cluster, _ = found
    articles = _articles_for_cluster(db_path, cluster)
    if not articles:
        print(f"No articles resolvable for cluster {cluster.id}")
        return 1

    packet = _build_packet_for_cluster(db_path, cluster, articles, args.series_config)

    visual_ir = load_visual_ir_for_script(db_path, script.id)
    if visual_ir is None:
        visual_ir = VisualPlanner().plan(script, plan, packet)
        upsert_visual_ir(db_path, visual_ir)

    manifest = QuoteManifestBuilder().build(
        script,
        visual_ir,
        packet,
        episode_id=plan.id,
    )
    output_dir = write_quote_manifest(manifest, quote_root=Path(args.quote_root))

    human_required = sum(
        1 for quote in manifest.quotes if quote.approval_state == "human_required"
    )
    by_type: dict[str, int] = {}
    for quote in manifest.quotes:
        by_type[quote.quote_type] = by_type.get(quote.quote_type, 0) + 1

    print(f"Quote manifest written: {manifest.episode_id}")
    print(f"Script: {script.id}  VisualIR: {visual_ir.id}")
    print(
        f"Quotes: {len(manifest.quotes)}  "
        f"human_required: {human_required}  by_type: {by_type}"
    )
    print(f"Output dir: {output_dir}")
    return 0


def cmd_visual(args: argparse.Namespace) -> int:
    if args.visual_command != "plan":
        print(f"Unsupported visual subcommand: {args.visual_command}")
        return 2

    db_path = Path(args.db)
    init_db(db_path)

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
    cluster, _ = found
    articles = _articles_for_cluster(db_path, cluster)
    if not articles:
        print(f"No articles resolvable for cluster {cluster.id}")
        return 1

    packet = _build_packet_for_cluster(db_path, cluster, articles, args.series_config)

    visual_ir = VisualPlanner().plan(script, plan, packet)
    upsert_visual_ir(db_path, visual_ir)
    output_dir = write_visual_bundle(visual_ir, script, plan, visual_root=Path(args.visual_root))

    human_required = sum(1 for u in visual_ir.visual_units if u.approval_state == "human_required")
    print(f"Visual plan built: {visual_ir.id}")
    print(f"Script: {script.id}  Plan: {plan.id}")
    print(f"Units: {len(visual_ir.visual_units)}  human_required: {human_required}")
    print(f"Output dir: {output_dir}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    if args.export_command == "inspect":
        return _cmd_export_inspect(args)
    if args.export_command == "ymm4":
        return _cmd_export_ymm4(args)
    print(f"Unsupported export subcommand: {args.export_command}")
    return 2


def _cmd_export_inspect(args: argparse.Namespace) -> int:
    inspection = inspect_episode_bundle(args.episode_dir)
    status = "PASS" if inspection.passed else "FAIL"
    print(f"Export bundle inspect: {status}")
    print(f"Episode dir: {inspection.episode_dir}")
    if inspection.errors:
        print("Errors:")
        for issue in inspection.errors:
            print(f"- [{issue.code}] {issue.message}")
    if inspection.warnings:
        print("Warnings:")
        for issue in inspection.warnings:
            print(f"- [{issue.code}] {issue.message}")
    if not inspection.issues:
        print("No issues found.")
    return 0 if inspection.passed else 1


def _cmd_export_ymm4(args: argparse.Namespace) -> int:
    db_path = Path(args.db)
    init_db(db_path)

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
    cluster, _ = found
    articles = _articles_for_cluster(db_path, cluster)
    if not articles:
        print(f"No articles resolvable for cluster {cluster.id}")
        return 1

    packet = _build_packet_for_cluster(db_path, cluster, articles, args.series_config)
    findings = ScriptCritic().critique(script, plan, packet)

    visual_ir = load_visual_ir_for_script(db_path, script.id)
    if visual_ir is None:
        visual_ir = VisualPlanner().plan(script, plan, packet)
        upsert_visual_ir(db_path, visual_ir)

    export_root = Path(args.export_root)
    episode_id = export_episode_id(plan, script)
    export_dir = export_root / episode_id
    asset_manifest = (
        load_asset_manifest(Path(args.asset_root) / plan.id / "asset_manifest.yml")
        or load_asset_manifest(export_dir / "asset_manifest.yml")
    )
    quote_manifest = (
        load_quote_manifest(Path(args.quote_root) / plan.id / "quote_manifest.yml")
        or load_quote_manifest(export_dir / "quote_manifest.yml")
    )

    output_dir, manifest = build_ymm4_package(
        plan,
        script,
        packet,
        findings,
        export_root=export_root,
        visual_ir=visual_ir,
        asset_manifest=asset_manifest,
        quote_manifest=quote_manifest,
    )

    print(f"YMM4 export ready: {manifest['episode_id']}")
    print(f"Output dir: {output_dir}")
    print(f"Format: {manifest['format']}")
    print(f"Warnings: {len(manifest['warnings'])}")
    for warning in manifest["warnings"]:
        print(f"  - {warning}")
    return 0


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)

    dispatchers = {
        "fetch": cmd_fetch,
        "report": cmd_report,
        "cluster": cmd_cluster,
        "score": cmd_score,
        "shortlist": cmd_shortlist,
        "series": cmd_series,
        "packet": cmd_packet,
        "script": cmd_script,
        "visual": cmd_visual,
        "asset": cmd_asset,
        "quote": cmd_quote,
        "export": cmd_export,
    }
    handler = dispatchers.get(args.command)
    if handler is None:
        parser.error(f"Unknown command: {args.command}")
        return 2
    return handler(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
