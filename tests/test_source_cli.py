from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

from newsroom.cli.main import main


def _rss_data_url() -> str:
    xml = (
        '<rss version="2.0"><channel>'
        '<title>Smoke Feed</title>'
        '<link>https://example.com/feed</link>'
        '<item><title>Smoke Topic</title>'
        '<link>https://example.com/smoke</link>'
        '<description>Smoke summary</description>'
        '<pubDate>Mon, 25 May 2026 09:00:00 +0900</pubDate>'
        '</item></channel></rss>'
    )
    return "data:application/rss+xml," + quote(xml, safe="")


def _write_opml(tmp_path: Path) -> Path:
    opml = tmp_path / "feeds.opml"
    opml.write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <body>
    <outline text="News">
      <outline text="Smoke Feed" xmlUrl="{_rss_data_url()}" />
    </outline>
  </body>
</opml>
""",
        encoding="utf-8",
    )
    return opml


def test_source_import_opml_outputs_review_disabled_yaml(tmp_path, capsys):
    opml = _write_opml(tmp_path)

    code = main(["source", "import-opml", "--opml", str(opml), "--format", "yaml"])

    assert code == 0
    out = capsys.readouterr().out
    assert "feeds:" in out
    assert "Smoke Feed" in out
    assert "enabled: false" in out
    assert "reader_categories:" in out


def test_source_smoke_opml_json_is_sanitized(tmp_path, capsys):
    opml = _write_opml(tmp_path)

    code = main(["source", "smoke", "--opml", str(opml), "--format", "json"])

    assert code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["input_kind"] == "OPML export"
    assert data["source_count"] == 1
    assert data["fetch_status_counts"] == {"fetched": 1, "empty": 0, "error": 0, "listed": 0}
    assert data["representative_article_fields"]["url"] == "present"
    assert data["representative_article_fields"]["summary"] == "present"
    assert "Smoke Topic" not in captured.out
    assert "https://example.com/smoke" not in captured.out
