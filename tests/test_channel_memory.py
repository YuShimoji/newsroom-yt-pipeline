from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from newsroom.editorial.channel_memory import (
    ChannelMemoryValidationError,
    load_channel_memory,
    render_channel_memory_report,
    validate_channel_memory_payload,
)
from newsroom.cli.main import main


def test_default_channel_memory_loads_active_episode():
    memory = load_channel_memory("docs/channel_memory/copilot_watch.yml")

    assert memory.series_id == "copilot_watch"
    assert memory.episodes[0].episode_id == "episode_756343df9853"
    assert memory.episodes[0].story_id == "story_20260603_503c39418f15862d"
    assert memory.episodes[0].script_id == "script_d2a46430e084"
    assert memory.episodes[0].packet_id == "packet_20260603_2de578dcd4b0"


def test_default_channel_memory_preserves_source_and_critical_fields():
    memory = load_channel_memory("docs/channel_memory/copilot_watch.yml")
    episode = memory.episodes[0]

    assert episode.source_roles_used[0].source_type == "official"
    assert episode.source_roles_used[0].article_ids == [
        "article_f4124bbb866ef6b0",
        "article_bfba4cd5131daa71",
    ]
    assert episode.critical_views_used[0].article_id == "article_bfba4cd5131daa71"
    assert episode.critical_views_used[0].source_name == "NIST"


def test_default_channel_memory_has_next_episode_seed():
    memory = load_channel_memory("docs/channel_memory/copilot_watch.yml")
    candidates = memory.episodes[0].followup_candidates

    assert [candidate.status for candidate in candidates] == ["seed", "seed"]
    assert "regulator_public" in candidates[0].source_roles_needed
    assert "critical_view_candidate" in candidates[1].source_roles_needed


def test_channel_memory_report_includes_readback_sections():
    memory = load_channel_memory("docs/channel_memory/copilot_watch.yml")

    report = render_channel_memory_report(memory)

    assert "Series: Copilot Watch (copilot_watch)" in report
    assert "Episodes: 1" in report
    assert "Episode episode_756343df9853" in report
    assert "Story: story_20260603_503c39418f15862d" in report
    assert "Script: script_d2a46430e084" in report
    assert "Packet: packet_20260603_2de578dcd4b0" in report
    assert "Source-role coverage:" in report
    assert "Critical views:" in report
    assert "NIST: article_bfba4cd5131daa71" in report
    assert "Compact claims:" in report
    assert "Open questions:" in report
    assert "Follow-up seeds:" in report
    assert "follow-up seeds are not approved stories" in report


def test_series_report_cli_prints_channel_memory(capsys):
    exit_code = main(["series", "report", "--series", "copilot_watch"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Series: Copilot Watch (copilot_watch)" in output
    assert "Episode episode_756343df9853" in output
    assert "follow-up seeds are not approved stories" in output


def test_channel_memory_rejects_raw_article_body(tmp_path):
    payload = _minimal_payload()
    payload["episodes"][0]["raw_article_body"] = "not tracked"
    path = tmp_path / "memory.yml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    with pytest.raises(ChannelMemoryValidationError, match="raw_article_body"):
        load_channel_memory(path)


def test_channel_memory_rejects_unknown_source_role():
    payload = _minimal_payload()
    payload["episodes"][0]["followup_candidates"][0]["source_roles_needed"] = [
        "broad_crawl"
    ]

    with pytest.raises(ValueError, match="source_role"):
        validate_channel_memory_payload(payload)


def _minimal_payload() -> dict:
    return {
        "artifact_type": "channel_memory",
        "schema_version": 1,
        "series_id": "copilot_watch",
        "title": "Copilot Watch",
        "status": "active",
        "episodes": [
            {
                "episode_id": "episode_1",
                "story_id": "story_1",
                "script_id": "script_1",
                "packet_id": "packet_1",
                "topic": "A source-bounded topic.",
                "status": "seed",
                "source_roles_used": [
                    {
                        "source_role": "vendor_official",
                        "source_pool_id": "microsoft_official",
                        "source_type": "official",
                        "source_count": 1,
                        "article_ids": ["article_1"],
                    }
                ],
                "critical_views_used": [],
                "claims_made": [
                    {
                        "claim_id": "claim_1",
                        "summary": "A compact claim summary.",
                        "source_refs": ["article_1"],
                        "critical_refs": [],
                    }
                ],
                "open_questions": ["What should be checked next?"],
                "followup_candidates": [
                    {
                        "candidate_id": "candidate_1",
                        "title": "Next seed",
                        "rationale": "Keep continuity visible.",
                        "source_roles_needed": ["vendor_official"],
                        "status": "seed",
                    }
                ],
            }
        ],
    }
