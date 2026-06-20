from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


FIXTURE_PATH = Path("samples/_probe/newsroom_handoff/newsroom_export_fixture_v1.json")
CONTRACT_PATH = Path("docs/integration/NEWSROOM_EXPORT_FIXTURE_FOR_NLMYTGEN_V1.md")

REQUIRED_FIELDS = {
    "episode_id",
    "title",
    "topic_summary",
    "source_notes",
    "provenance",
    "rights_summary",
    "notebooklm_packet",
    "script_beats",
    "visual_plan",
    "g28_slot_hints",
    "review_warnings",
    "downstream_readiness",
    "export_metadata",
    "source_confidence",
    "editorial_priority",
    "reviewer_notes",
    "localization_notes",
    "channel_metadata",
}

CONTRACT_KEYS = {
    "field",
    "owner",
    "required_before",
    "source_within_newsroom",
    "fake_fixture_value",
    "nlmytgen_expected_consumer",
    "failure_behavior",
    "implementation_status",
    "next_action",
}

ALLOWED_REQUIRED_BEFORE = {
    "NLMYTGen ingest",
    "transfer candidate",
    "human review",
    "optional enrichment",
}
ALLOWED_FAILURE_BEHAVIOR = {
    "fail",
    "warn",
    "block_transfer",
    "hold_for_review",
}
ALLOWED_IMPLEMENTATION_STATUS = {
    "present",
    "fake_only",
    "missing",
    "policy_only",
}
URL_PATTERN = re.compile(r"https?://", re.IGNORECASE)


def _fixture() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _walk_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _walk_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_strings(child)


def test_newsroom_export_fixture_parses_and_has_required_categories():
    payload = _fixture()

    assert payload["schema_version"] == "newsroom_export_fixture.v1"
    assert REQUIRED_FIELDS <= payload.keys()
    assert payload["review_status"] == "fake_only_contract_probe"
    assert payload["downstream_readiness"]["production_ymm4"] == "fail"


def test_newsroom_export_fixture_has_complete_field_contract():
    payload = _fixture()
    contract = payload["field_contract"]

    assert isinstance(contract, list)
    assert {entry["field"] for entry in contract} == REQUIRED_FIELDS
    for entry in contract:
        assert CONTRACT_KEYS <= entry.keys()
        assert set(entry["required_before"]) <= ALLOWED_REQUIRED_BEFORE
        assert entry["failure_behavior"] in ALLOWED_FAILURE_BEHAVIOR
        assert entry["implementation_status"] in ALLOWED_IMPLEMENTATION_STATUS
        assert entry["owner"]
        assert entry["nlmytgen_expected_consumer"]


def test_newsroom_export_fixture_contains_no_real_urls_or_media():
    payload = _fixture()

    assert payload["export_metadata"]["contains_real_news"] is False
    assert payload["export_metadata"]["contains_credentials"] is False
    assert payload["export_metadata"]["contains_media"] is False
    assert payload["export_metadata"]["contains_external_downloads"] is False
    assert all(not URL_PATTERN.search(text) for text in _walk_strings(payload))
    assert not URL_PATTERN.search(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_newsroom_export_fixture_keeps_downstream_responsibilities_narrow():
    payload = _fixture()
    boundary = payload["boundary_assertions"]

    assert boundary["rss_source_discovery_owner"] == "newsroom-yt-pipeline"
    assert boundary["production_readiness_implied"] is False
    assert boundary["ymm4_geometry_authority"] == "downstream_nlmytgen"
    assert "scrape_articles" in boundary["nlmytgen_must_not"]
    assert "infer_missing_rights" in boundary["nlmytgen_must_not"]
    assert "fetch_external_urls" in boundary["nlmytgen_must_not"]


def test_newsroom_export_fixture_contract_doc_mentions_required_boundaries():
    body = CONTRACT_PATH.read_text(encoding="utf-8")

    assert "RSS/source discovery remains newsroom-side" in body
    assert "NLMYTGen should not scrape articles" in body
    assert "fake fixture does not mean real packet approval" in body
    assert "No production, publication, YMM4 import" in body
