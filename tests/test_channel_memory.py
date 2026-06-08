from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from newsroom.editorial.channel_memory import (
    ChannelMemoryValidationError,
    append_episode_record,
    load_channel_memory,
    load_episode_record_payload,
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
    roles_by_pool = {role.source_pool_id: role for role in episode.source_roles_used}

    assert set(roles_by_pool) == {"microsoft_official", "standards_body"}
    assert roles_by_pool["microsoft_official"].source_role == "vendor_official"
    assert roles_by_pool["microsoft_official"].source_type == "official"
    assert roles_by_pool["microsoft_official"].article_ids == [
        "article_f4124bbb866ef6b0"
    ]
    assert roles_by_pool["standards_body"].source_role == "standards_body"
    assert roles_by_pool["standards_body"].source_type == "official"
    assert roles_by_pool["standards_body"].article_ids == [
        "article_bfba4cd5131daa71"
    ]

    critical = episode.critical_views_used[0]
    assert critical.article_id == "article_bfba4cd5131daa71"
    assert critical.source_name == "NIST"
    assert critical.source_role == "standards_body"
    assert critical.source_pool_id == "standards_body"


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
    assert (
        "vendor_official / microsoft_official / official: "
        "1 source(s) [article_f4124bbb866ef6b0]"
    ) in report
    assert (
        "standards_body / standards_body / official: "
        "1 source(s) [article_bfba4cd5131daa71]"
    ) in report
    assert "unclassified / no_pool" not in report
    assert "Critical views:" in report
    assert "NIST: article_bfba4cd5131daa71" in report
    assert "[official, standards_body]" in report
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
    assert "vendor_official / microsoft_official" in output
    assert "standards_body / standards_body" in output
    assert "unclassified / no_pool" not in output
    assert "follow-up seeds are not approved stories" in output


def test_default_channel_memory_does_not_store_forbidden_payload_fields():
    payload = yaml.safe_load(
        Path("docs/channel_memory/copilot_watch.yml").read_text(encoding="utf-8")
    )

    for forbidden in (
        "article_body",
        "approved_text",
        "body_text",
        "private_data",
        "raw_article_body",
        "runtime_db_path",
        "screenshot_path",
        "subtitle_coordinates",
        "ymmp",
        "ymm4_geometry",
    ):
        assert not _contains_key(payload, forbidden)


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


def test_append_episode_record_adds_valid_episode(tmp_path):
    memory_path = _write_yaml(tmp_path / "copilot_watch.yml", _minimal_payload())
    record_path = _write_yaml(tmp_path / "episode_record.yml", _episode_record())

    memory = append_episode_record(memory_path, record_path)

    assert len(memory.episodes) == 2
    assert memory.episodes[1].episode_id == "episode_2"
    assert memory.episodes[1].followup_candidates[0].status == "seed"
    report = render_channel_memory_report(memory)
    assert "Episodes: 2" in report
    assert "Episode episode_2" in report
    assert "[seed] candidate_2" in report


def test_append_episode_record_rejects_duplicate_episode_id(tmp_path):
    memory_path = _write_yaml(tmp_path / "copilot_watch.yml", _minimal_payload())
    record = _episode_record()
    record["episode_id"] = "episode_1"
    record_path = _write_yaml(tmp_path / "episode_record.yml", record)

    with pytest.raises(ChannelMemoryValidationError, match="duplicate episode_id"):
        append_episode_record(memory_path, record_path)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("story_id", "story_1", "duplicate story_id"),
        ("script_id", "script_1", "duplicate script_id"),
        ("packet_id", "packet_1", "duplicate packet_id"),
    ],
)
def test_append_episode_record_rejects_duplicate_story_script_packet_ids(
    tmp_path, field, value, message
):
    memory_path = _write_yaml(tmp_path / "copilot_watch.yml", _minimal_payload())
    record = _episode_record()
    record[field] = value
    record_path = _write_yaml(tmp_path / "episode_record.yml", record)

    with pytest.raises(ChannelMemoryValidationError, match=message):
        append_episode_record(memory_path, record_path)


def test_episode_record_rejects_forbidden_and_unknown_fields(tmp_path):
    record = _episode_record()
    record["runtime_db_path"] = "data/newsroom.sqlite"
    record_path = _write_yaml(tmp_path / "episode_record.yml", record)

    with pytest.raises(ChannelMemoryValidationError, match="runtime_db_path"):
        load_episode_record_payload(record_path)

    record = _episode_record()
    record["export_manifest"] = "data/exports/episode_2/export_manifest.json"
    record_path = _write_yaml(tmp_path / "episode_record.yml", record)

    with pytest.raises(ChannelMemoryValidationError, match="unsupported keys"):
        load_episode_record_payload(record_path)


def test_followup_candidate_status_must_remain_seed():
    payload = _minimal_payload()
    payload["episodes"][0]["followup_candidates"][0]["status"] = "approved_story"

    with pytest.raises(ChannelMemoryValidationError, match="must be 'seed'"):
        validate_channel_memory_payload(payload)


def test_series_append_episode_cli_writes_memory_and_keeps_report_stable(tmp_path, capsys):
    memory_root = tmp_path / "memory"
    memory_root.mkdir()
    _write_yaml(memory_root / "copilot_watch.yml", _minimal_payload())
    record_path = _write_yaml(tmp_path / "episode_record.yml", _episode_record())

    exit_code = main(
        [
            "series",
            "append-episode",
            "--series",
            "copilot_watch",
            "--memory-root",
            str(memory_root),
            "--episode-record",
            str(record_path),
        ]
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Episodes: 2" in output
    assert "follow-up seeds remain seeds" in output

    exit_code = main(
        [
            "series",
            "report",
            "--series",
            "copilot_watch",
            "--memory-root",
            str(memory_root),
        ]
    )
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Episodes: 2" in output
    assert "Episode episode_2" in output
    assert "[seed] candidate_2" in output


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


def _episode_record() -> dict:
    return {
        "artifact_type": "channel_memory_episode",
        "schema_version": 1,
        "episode_id": "episode_2",
        "story_id": "story_2",
        "script_id": "script_2",
        "packet_id": "packet_2",
        "topic": "A second source-bounded topic.",
        "status": "newsroom_handoff_clean",
        "source_roles_used": [
            {
                "source_role": "vendor_official",
                "source_pool_id": "microsoft_official",
                "source_type": "official",
                "source_count": 1,
                "article_ids": ["article_2"],
            }
        ],
        "critical_views_used": [
            {
                "article_id": "article_3",
                "source_name": "Regulator",
                "source_type": "official",
                "source_role": "regulator_public",
                "source_pool_id": "regulator_public",
                "title": "Public oversight note",
                "purpose": "Keep the story bounded by public risk framing.",
            }
        ],
        "claims_made": [
            {
                "claim_id": "claim_2",
                "summary": "A compact second-episode claim summary.",
                "source_refs": ["article_2"],
                "critical_refs": ["article_3"],
            }
        ],
        "open_questions": ["What source should be paired next?"],
        "followup_candidates": [
            {
                "candidate_id": "candidate_2",
                "title": "Next seed",
                "rationale": "Keep the trail visible without selecting a story.",
                "source_roles_needed": ["vendor_official", "regulator_public"],
                "status": "seed",
            }
        ],
    }


def _write_yaml(path: Path, payload: dict) -> Path:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def _contains_key(value: object, key: str) -> bool:
    if isinstance(value, dict):
        return key in value or any(_contains_key(child, key) for child in value.values())
    if isinstance(value, list):
        return any(_contains_key(item, key) for item in value)
    return False
