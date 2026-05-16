from __future__ import annotations

from newsroom.cli.main import main
from newsroom.store.db import upsert_article
from newsroom.store.models import Article


def test_report_today_outputs_candidates(tmp_path, capsys):
    db_path = tmp_path / "newsroom.sqlite"
    article = Article.create(
        url="https://example.com/a",
        title="Candidate Article",
        source_name="Example",
        source_type="official",
        published_at="2026-05-16T01:00:00+00:00",
        fetched_at="2026-05-16T02:00:00+00:00",
    )
    upsert_article(db_path, article)

    exit_code = main(["--db", str(db_path), "report", "--date", "2026-05-16"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Newsroom report for 2026-05-16" in output
    assert "Candidate Article" in output
    assert "score_components" in output

