from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from newsroom.store.models import Article, SourceFeed


@dataclass(frozen=True)
class SourceSmokeResult:
    source_id: str
    status: str
    entry_count: int = 0
    shown_count: int = 0
    error: str | None = None


def build_source_smoke_evidence(
    *,
    input_kind: str,
    sources: list[SourceFeed],
    results: list[SourceSmokeResult],
    representative_articles: list[Article],
) -> dict[str, object]:
    status_counts = Counter(result.status for result in results)
    categories = {
        tag
        for source in sources
        for tag in [*source.tags, *source.reader_categories]
        if tag
    }
    has_sources = bool(sources)
    has_articles = bool(representative_articles)
    has_errors = bool(status_counts.get("error"))

    return {
        "input_kind": input_kind,
        "source_count": len(sources),
        "enabled_source_count": sum(1 for source in sources if source.enabled),
        "category_count": len(categories),
        "source_list_match": "manual_required" if has_sources else "blocked_no_sources",
        "fetch_status_counts": {
            "fetched": status_counts.get("fetched", 0),
            "empty": status_counts.get("empty", 0),
            "error": status_counts.get("error", 0),
            "listed": status_counts.get("listed", 0),
        },
        "representative_article_fields": _representative_article_fields(
            representative_articles[0] if representative_articles else None
        ),
        "notable_fixes_needed": _fix_notes(has_sources, has_articles, has_errors),
        "next_move": _next_move(input_kind, has_sources, has_articles, has_errors),
        "manual_hands_on": _manual_hands_on(input_kind),
    }


def render_source_smoke_markdown(evidence: dict[str, object]) -> str:
    counts = evidence["fetch_status_counts"]
    assert isinstance(counts, dict)
    fields = evidence["representative_article_fields"]
    assert isinstance(fields, dict)
    fixes = evidence["notable_fixes_needed"]
    assert isinstance(fixes, list)
    manual = evidence["manual_hands_on"]
    assert isinstance(manual, list)

    lines = [
        "# Source Smoke Evidence",
        "",
        f"- input kind: {evidence['input_kind']}",
        f"- source count: {evidence['source_count']}",
        f"- enabled source count: {evidence['enabled_source_count']}",
        f"- category count: {evidence['category_count']}",
        f"- source list match: {evidence['source_list_match']}",
        (
            "- fetch status counts: "
            f"fetched={counts.get('fetched', 0)}, "
            f"empty={counts.get('empty', 0)}, "
            f"error={counts.get('error', 0)}, "
            f"listed={counts.get('listed', 0)}"
        ),
        "",
        "## Representative Article Fields",
        "",
    ]
    for key in sorted(fields):
        lines.append(f"- {key}: {fields[key]}")
    lines.extend(["", "## Notable Fixes Needed", ""])
    if fixes:
        lines.extend(f"- {fix}" for fix in fixes)
    else:
        lines.append("- none")
    lines.extend(["", "## Next Move", "", str(evidence["next_move"]), "", "## Manual Hands-On", ""])
    lines.extend(f"- {item}" for item in manual)
    return "\n".join(lines) + "\n"


def _representative_article_fields(article: Article | None) -> dict[str, str]:
    if article is None:
        return {
            "url": "absent",
            "summary": "absent",
            "published_at": "absent",
            "source_role": "absent",
            "source_pool_id": "absent",
        }
    return {
        "url": _presence(article.url),
        "summary": _presence(article.summary),
        "published_at": _presence(article.published_at),
        "source_role": _presence(article.source_role),
        "source_pool_id": _presence(article.source_pool_id),
    }


def _presence(value: object | None) -> str:
    return "present" if value not in (None, "", [], ()) else "absent"


def _fix_notes(has_sources: bool, has_articles: bool, has_errors: bool) -> list[str]:
    notes: list[str] = []
    if not has_sources:
        notes.append("no sources were available for smoke")
    if not has_articles:
        notes.append("no representative article was fetched")
    if has_errors:
        notes.append("one or more sources failed to fetch")
    return notes


def _next_move(input_kind: str, has_sources: bool, has_articles: bool, has_errors: bool) -> str:
    if not has_sources:
        return "import or configure source feeds before running the editorial pipeline"
    if has_errors and not has_articles:
        return "fix or disable failing sources before treating this source set as ready"
    if input_kind.startswith("OPML"):
        return "compare source and category counts against the human reader, then import reviewed feeds into sources.yml"
    if input_kind.startswith("Inoreader"):
        return "compare counts against the Inoreader UI, then decide whether read-only token flow is acceptable"
    return "continue with fetch -> cluster -> score after reviewing source coverage"


def _manual_hands_on(input_kind: str) -> list[str]:
    if input_kind.startswith("OPML"):
        return [
            "Export OPML from the human RSS reader outside the repo.",
            "Compare source_count and category_count with the reader UI.",
            "Commit only sanitized evidence or reviewed source config, not raw OPML.",
        ]
    if input_kind.startswith("Inoreader"):
        return [
            "Provide a temporary access token through the configured environment variable.",
            "Compare source_count/category_count with the Inoreader UI.",
            "Do not commit tokens, raw stream payloads, private feed URLs, or article bodies.",
        ]
    return [
        "Review failing source count before clustering.",
        "Keep raw article bodies out of tracked artifacts unless a later policy explicitly allows them.",
    ]
