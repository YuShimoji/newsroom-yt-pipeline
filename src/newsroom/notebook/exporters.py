from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from newsroom.store.models import NotebookPacket


def write_packet(packet: NotebookPacket) -> Path:
    """Render the packet artifact bundle to disk and return its directory."""
    output_dir = Path(packet.export_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "packet.md").write_text(_render_packet_md(packet), encoding="utf-8")
    (output_dir / "sources.json").write_text(_render_sources_json(packet), encoding="utf-8")
    (output_dir / "timeline.md").write_text(_render_timeline_md(packet), encoding="utf-8")
    (output_dir / "glossary.md").write_text(_render_glossary_md(packet), encoding="utf-8")
    (output_dir / "questions.md").write_text(_render_questions_md(packet), encoding="utf-8")
    (output_dir / "operator_notes.md").write_text(_render_operator_md(packet), encoding="utf-8")
    return output_dir


def _render_packet_md(packet: NotebookPacket) -> str:
    lines: list[str] = []
    lines.append(f"# NotebookLM Packet — {packet.story_cluster_id}")
    lines.append("")
    lines.append(f"- packet_id: `{packet.id}`")
    lines.append(f"- format_hint: `{packet.format_hint}`")
    lines.append(f"- created_at: {packet.created_at}")
    lines.append("")
    lines.append("This bundle is intended for manual upload to NotebookLM. "
                 "Do not treat its outputs as a finished script.")
    lines.append("")
    lines.append("## Primary sources")
    if packet.primary_sources:
        for ref in packet.primary_sources:
            lines.append(f"- [{ref.title}]({ref.url}) — {ref.source_name} ({ref.published_at or 'date unknown'})")
    else:
        lines.append("_None._")
    lines.append("")
    lines.append("## News sources")
    if packet.news_sources:
        for ref in packet.news_sources:
            lines.append(f"- [{ref.title}]({ref.url}) — {ref.source_name} ({ref.published_at or 'date unknown'})")
    else:
        lines.append("_None._")
    lines.append("")
    lines.append("## Companion files")
    lines.append("- `sources.json` — machine-readable source list")
    lines.append("- `timeline.md` — chronological event list")
    lines.append("- `glossary.md` — entities and terms to define")
    lines.append("- `questions.md` — angles to feed NotebookLM")
    lines.append("- `operator_notes.md` — review checklist for the operator")
    lines.append("")
    return "\n".join(lines)


def _render_sources_json(packet: NotebookPacket) -> str:
    payload = {
        "packet_id": packet.id,
        "story_cluster_id": packet.story_cluster_id,
        "primary_sources": [asdict(ref) for ref in packet.primary_sources],
        "news_sources": [asdict(ref) for ref in packet.news_sources],
        "critical_views": [asdict(ref) for ref in packet.critical_views],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def _render_timeline_md(packet: NotebookPacket) -> str:
    lines = ["# Timeline", ""]
    if not packet.timeline:
        lines.append("_No timeline events._")
        return "\n".join(lines) + "\n"
    for event in packet.timeline:
        date = event.occurred_at or "date unknown"
        lines.append(f"- {date} — **{event.source_name}**: [{event.title}]({event.url})")
    return "\n".join(lines) + "\n"


def _render_glossary_md(packet: NotebookPacket) -> str:
    lines = ["# Glossary", ""]
    if not packet.glossary:
        lines.append("_No entities extracted; add terms manually before NotebookLM upload._")
        return "\n".join(lines) + "\n"
    for term in packet.glossary:
        definition = term.definition or "_(definition TBD — operator fills in)_"
        lines.append(f"- **{term.term}**: {definition}")
    return "\n".join(lines) + "\n"


def _render_questions_md(packet: NotebookPacket) -> str:
    lines = ["# Questions for NotebookLM", ""]
    for index, question in enumerate(packet.questions, start=1):
        lines.append(f"{index}. {question}")
    return "\n".join(lines) + "\n"


def _render_operator_md(packet: NotebookPacket) -> str:
    lines: list[str] = []
    lines.append(f"# Operator Notes — {packet.id}")
    lines.append("")
    lines.append(f"- Format hint: `{packet.format_hint}` (override if the angle changes)")
    lines.append(f"- Primary source count: {len(packet.primary_sources)}")
    lines.append(f"- News source count: {len(packet.news_sources)}")
    lines.append("")
    lines.append("## Review checklist before NotebookLM upload")
    lines.append("- [ ] Confirm each source is reachable and quote-friendly.")
    lines.append("- [ ] Verify no primary source requires special licensing.")
    lines.append("- [ ] Add at least one critical-view source manually if the cluster lacks one.")
    lines.append("- [ ] Fill in glossary definitions for any unfamiliar term.")
    lines.append("- [ ] Adjust the questions if the editorial angle shifts.")
    lines.append("")
    return "\n".join(lines)
