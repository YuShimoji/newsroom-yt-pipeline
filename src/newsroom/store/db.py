from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from newsroom.store.models import (
    Article,
    Chapter,
    EpisodePlan,
    ScriptIR,
    ScriptSegment,
    StoryCluster,
    TopicScore,
    VisualIR,
    VisualUnit,
)


DEFAULT_DB_PATH = Path("data/newsroom.sqlite")


SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
  id TEXT PRIMARY KEY,
  url TEXT NOT NULL,
  canonical_url TEXT,
  title TEXT NOT NULL,
  source_name TEXT NOT NULL,
  source_url TEXT,
  author TEXT,
  published_at TEXT,
  fetched_at TEXT NOT NULL,
  body_text TEXT,
  summary TEXT,
  language TEXT,
  tags TEXT NOT NULL,
  source_type TEXT NOT NULL,
  license_hint TEXT,
  hash_url TEXT NOT NULL UNIQUE,
  hash_title TEXT NOT NULL,
  hash_body TEXT,
  fetch_status TEXT NOT NULL,
  fetch_error TEXT
);

CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at);
CREATE INDEX IF NOT EXISTS idx_articles_fetched_at ON articles(fetched_at);
CREATE INDEX IF NOT EXISTS idx_articles_source_name ON articles(source_name);

CREATE TABLE IF NOT EXISTS story_clusters (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  summary TEXT,
  primary_sources TEXT NOT NULL,
  related_series TEXT NOT NULL,
  entities TEXT NOT NULL,
  content_farm_overlap REAL NOT NULL DEFAULT 0.0,
  cluster_date TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_clusters_date ON story_clusters(cluster_date);

CREATE TABLE IF NOT EXISTS cluster_articles (
  cluster_id TEXT NOT NULL,
  article_id TEXT NOT NULL,
  PRIMARY KEY (cluster_id, article_id),
  FOREIGN KEY (cluster_id) REFERENCES story_clusters(id),
  FOREIGN KEY (article_id) REFERENCES articles(id)
);

CREATE INDEX IF NOT EXISTS idx_cluster_articles_cluster ON cluster_articles(cluster_id);
CREATE INDEX IF NOT EXISTS idx_cluster_articles_article ON cluster_articles(article_id);

CREATE TABLE IF NOT EXISTS topic_scores (
  cluster_id TEXT PRIMARY KEY,
  score_total REAL NOT NULL,
  components TEXT NOT NULL,
  scored_at TEXT NOT NULL,
  FOREIGN KEY (cluster_id) REFERENCES story_clusters(id)
);

CREATE TABLE IF NOT EXISTS episode_plans (
  id TEXT PRIMARY KEY,
  story_cluster_id TEXT NOT NULL,
  series_id TEXT,
  title_candidates TEXT NOT NULL,
  thumbnail_angles TEXT NOT NULL,
  hook TEXT NOT NULL,
  chapter_outline TEXT NOT NULL,
  target_duration_sec INTEGER NOT NULL,
  viewer_utility TEXT NOT NULL,
  risk_notes TEXT NOT NULL,
  approval_state TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_episode_plans_cluster ON episode_plans(story_cluster_id);

CREATE TABLE IF NOT EXISTS script_irs (
  id TEXT PRIMARY KEY,
  episode_plan_id TEXT NOT NULL,
  format TEXT NOT NULL,
  segments TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (episode_plan_id) REFERENCES episode_plans(id)
);

CREATE INDEX IF NOT EXISTS idx_script_irs_plan ON script_irs(episode_plan_id);

CREATE TABLE IF NOT EXISTS visual_irs (
  id TEXT PRIMARY KEY,
  script_id TEXT NOT NULL,
  visual_units TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (script_id) REFERENCES script_irs(id)
);

CREATE INDEX IF NOT EXISTS idx_visual_irs_script ON visual_irs(script_id);
"""


def connect(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path: str | Path = DEFAULT_DB_PATH) -> None:
    with connect(db_path) as connection:
        connection.executescript(SCHEMA)


def upsert_article(db_path: str | Path, article: Article) -> None:
    init_db(db_path)
    values = _article_values(article)
    with connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO articles (
              id, url, canonical_url, title, source_name, source_url, author,
              published_at, fetched_at, body_text, summary, language, tags,
              source_type, license_hint, hash_url, hash_title, hash_body,
              fetch_status, fetch_error
            )
            VALUES (
              :id, :url, :canonical_url, :title, :source_name, :source_url, :author,
              :published_at, :fetched_at, :body_text, :summary, :language, :tags,
              :source_type, :license_hint, :hash_url, :hash_title, :hash_body,
              :fetch_status, :fetch_error
            )
            ON CONFLICT(hash_url) DO UPDATE SET
              title = excluded.title,
              source_name = excluded.source_name,
              source_url = excluded.source_url,
              author = excluded.author,
              published_at = excluded.published_at,
              fetched_at = excluded.fetched_at,
              body_text = excluded.body_text,
              summary = excluded.summary,
              language = excluded.language,
              tags = excluded.tags,
              source_type = excluded.source_type,
              license_hint = excluded.license_hint,
              hash_title = excluded.hash_title,
              hash_body = excluded.hash_body,
              fetch_status = excluded.fetch_status,
              fetch_error = excluded.fetch_error
            """,
            values,
        )


def list_articles_for_date(db_path: str | Path, date_yyyy_mm_dd: str) -> list[Article]:
    init_db(db_path)
    with connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT * FROM articles
            WHERE substr(COALESCE(published_at, fetched_at), 1, 10) = ?
            ORDER BY COALESCE(published_at, fetched_at) DESC, source_name, title
            """,
            (date_yyyy_mm_dd,),
        ).fetchall()
    return [_row_to_article(row) for row in rows]


def list_articles_by_ids(
    db_path: str | Path, article_ids: list[str] | set[str]
) -> list[Article]:
    """Fetch articles by id regardless of their published_at date.

    Story clusters that span a multi-day window contain article ids whose
    published_at can fall on any day in the window. Resolving cluster
    members by id avoids re-querying by date and keeps lookup correct
    when the cluster_date diverges from the member dates.
    """
    ids = list(article_ids)
    if not ids:
        return []
    init_db(db_path)
    placeholders = ",".join("?" for _ in ids)
    with connect(db_path) as connection:
        rows = connection.execute(
            f"SELECT * FROM articles WHERE id IN ({placeholders})",
            ids,
        ).fetchall()
    return [_row_to_article(row) for row in rows]


def list_articles_in_date_range(
    db_path: str | Path, start_date: str, end_date: str
) -> list[Article]:
    """Return articles whose published_at (or fetched_at fallback) lies in [start_date, end_date].

    Both endpoints are inclusive. Used by `newsroom cluster --days N` /
    `--from --to` to widen the clustering window beyond a single day.
    """
    init_db(db_path)
    with connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT * FROM articles
            WHERE substr(COALESCE(published_at, fetched_at), 1, 10) BETWEEN ? AND ?
            ORDER BY COALESCE(published_at, fetched_at) DESC, source_name, title
            """,
            (start_date, end_date),
        ).fetchall()
    return [_row_to_article(row) for row in rows]


def count_articles(db_path: str | Path) -> int:
    init_db(db_path)
    with connect(db_path) as connection:
        row = connection.execute("SELECT COUNT(*) AS count FROM articles").fetchone()
    return int(row["count"])


def replace_clusters_for_date(
    db_path: str | Path, cluster_date: str, clusters: list[StoryCluster]
) -> None:
    """Replace the cluster set for a given date.

    Daily clustering is deterministic over the day's articles, so a fresh
    run overwrites prior clusters for that date rather than accumulating.
    """
    init_db(db_path)
    with connect(db_path) as connection:
        old_ids = [
            row["id"]
            for row in connection.execute(
                "SELECT id FROM story_clusters WHERE cluster_date = ?",
                (cluster_date,),
            ).fetchall()
        ]
        if old_ids:
            placeholders = ",".join("?" for _ in old_ids)
            connection.execute(
                f"DELETE FROM topic_scores WHERE cluster_id IN ({placeholders})",
                old_ids,
            )
            connection.execute(
                f"DELETE FROM cluster_articles WHERE cluster_id IN ({placeholders})",
                old_ids,
            )
            connection.execute(
                "DELETE FROM story_clusters WHERE cluster_date = ?",
                (cluster_date,),
            )

        for cluster in clusters:
            connection.execute(
                """
                INSERT INTO story_clusters (
                  id, title, summary, primary_sources, related_series, entities,
                  content_farm_overlap, cluster_date, created_at, updated_at
                ) VALUES (
                  :id, :title, :summary, :primary_sources, :related_series, :entities,
                  :content_farm_overlap, :cluster_date, :created_at, :updated_at
                )
                """,
                _cluster_values(cluster),
            )
            connection.executemany(
                "INSERT INTO cluster_articles (cluster_id, article_id) VALUES (?, ?)",
                [(cluster.id, article_id) for article_id in cluster.article_ids],
            )


def list_clusters_for_date(db_path: str | Path, cluster_date: str) -> list[StoryCluster]:
    init_db(db_path)
    with connect(db_path) as connection:
        cluster_rows = connection.execute(
            """
            SELECT * FROM story_clusters
            WHERE cluster_date = ?
            ORDER BY created_at, id
            """,
            (cluster_date,),
        ).fetchall()
        clusters: list[StoryCluster] = []
        for row in cluster_rows:
            article_rows = connection.execute(
                "SELECT article_id FROM cluster_articles WHERE cluster_id = ? ORDER BY article_id",
                (row["id"],),
            ).fetchall()
            clusters.append(_row_to_cluster(row, [r["article_id"] for r in article_rows]))
    return clusters


def upsert_topic_score(db_path: str | Path, score: TopicScore) -> None:
    init_db(db_path)
    with connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO topic_scores (cluster_id, score_total, components, scored_at)
            VALUES (:cluster_id, :score_total, :components, :scored_at)
            ON CONFLICT(cluster_id) DO UPDATE SET
              score_total = excluded.score_total,
              components = excluded.components,
              scored_at = excluded.scored_at
            """,
            {
                "cluster_id": score.cluster_id,
                "score_total": score.score_total,
                "components": json.dumps(score.components, ensure_ascii=False),
                "scored_at": score.scored_at,
            },
        )


def list_topic_scores_for_date(
    db_path: str | Path, cluster_date: str
) -> list[TopicScore]:
    init_db(db_path)
    with connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT topic_scores.* FROM topic_scores
            JOIN story_clusters ON story_clusters.id = topic_scores.cluster_id
            WHERE story_clusters.cluster_date = ?
            ORDER BY topic_scores.score_total DESC
            """,
            (cluster_date,),
        ).fetchall()
    return [
        TopicScore(
            cluster_id=row["cluster_id"],
            score_total=row["score_total"],
            components=json.loads(row["components"]),
            scored_at=row["scored_at"],
        )
        for row in rows
    ]


def upsert_episode_plan(db_path: str | Path, plan: EpisodePlan) -> None:
    init_db(db_path)
    with connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO episode_plans (
              id, story_cluster_id, series_id, title_candidates, thumbnail_angles,
              hook, chapter_outline, target_duration_sec, viewer_utility,
              risk_notes, approval_state, created_at
            ) VALUES (
              :id, :story_cluster_id, :series_id, :title_candidates, :thumbnail_angles,
              :hook, :chapter_outline, :target_duration_sec, :viewer_utility,
              :risk_notes, :approval_state, :created_at
            )
            ON CONFLICT(id) DO UPDATE SET
              series_id = excluded.series_id,
              title_candidates = excluded.title_candidates,
              thumbnail_angles = excluded.thumbnail_angles,
              hook = excluded.hook,
              chapter_outline = excluded.chapter_outline,
              target_duration_sec = excluded.target_duration_sec,
              viewer_utility = excluded.viewer_utility,
              risk_notes = excluded.risk_notes,
              approval_state = excluded.approval_state
            """,
            _episode_plan_values(plan),
        )


def load_episode_plan(db_path: str | Path, plan_id: str) -> EpisodePlan | None:
    init_db(db_path)
    with connect(db_path) as connection:
        row = connection.execute(
            "SELECT * FROM episode_plans WHERE id = ?", (plan_id,)
        ).fetchone()
    if row is None:
        return None
    return _row_to_episode_plan(row)


def upsert_script_ir(db_path: str | Path, script: ScriptIR) -> None:
    init_db(db_path)
    with connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO script_irs (id, episode_plan_id, format, segments, created_at)
            VALUES (:id, :episode_plan_id, :format, :segments, :created_at)
            ON CONFLICT(id) DO UPDATE SET
              episode_plan_id = excluded.episode_plan_id,
              format = excluded.format,
              segments = excluded.segments
            """,
            {
                "id": script.id,
                "episode_plan_id": script.episode_plan_id,
                "format": script.format,
                "segments": json.dumps(
                    [_segment_to_dict(seg) for seg in script.segments],
                    ensure_ascii=False,
                ),
                "created_at": script.created_at,
            },
        )


def load_script_ir(db_path: str | Path, script_id: str) -> ScriptIR | None:
    init_db(db_path)
    with connect(db_path) as connection:
        row = connection.execute(
            "SELECT * FROM script_irs WHERE id = ?", (script_id,)
        ).fetchone()
    if row is None:
        return None
    raw_segments = json.loads(row["segments"] or "[]")
    segments = [_dict_to_segment(payload) for payload in raw_segments]
    return ScriptIR(
        id=row["id"],
        episode_plan_id=row["episode_plan_id"],
        format=row["format"],
        segments=segments,
        created_at=row["created_at"],
    )


def upsert_visual_ir(db_path: str | Path, visual_ir: VisualIR) -> None:
    init_db(db_path)
    with connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO visual_irs (id, script_id, visual_units, created_at)
            VALUES (:id, :script_id, :visual_units, :created_at)
            ON CONFLICT(id) DO UPDATE SET
              script_id = excluded.script_id,
              visual_units = excluded.visual_units
            """,
            {
                "id": visual_ir.id,
                "script_id": visual_ir.script_id,
                "visual_units": json.dumps(
                    [_visual_unit_to_dict(unit) for unit in visual_ir.visual_units],
                    ensure_ascii=False,
                ),
                "created_at": visual_ir.created_at,
            },
        )


def load_visual_ir(db_path: str | Path, visual_ir_id: str) -> VisualIR | None:
    init_db(db_path)
    with connect(db_path) as connection:
        row = connection.execute(
            "SELECT * FROM visual_irs WHERE id = ?", (visual_ir_id,)
        ).fetchone()
    if row is None:
        return None
    raw_units = json.loads(row["visual_units"] or "[]")
    units = [_dict_to_visual_unit(payload) for payload in raw_units]
    return VisualIR(
        id=row["id"],
        script_id=row["script_id"],
        visual_units=units,
        created_at=row["created_at"],
    )


def load_visual_ir_for_script(db_path: str | Path, script_id: str) -> VisualIR | None:
    init_db(db_path)
    with connect(db_path) as connection:
        row = connection.execute(
            "SELECT * FROM visual_irs WHERE script_id = ? ORDER BY created_at DESC LIMIT 1",
            (script_id,),
        ).fetchone()
    if row is None:
        return None
    raw_units = json.loads(row["visual_units"] or "[]")
    units = [_dict_to_visual_unit(payload) for payload in raw_units]
    return VisualIR(
        id=row["id"],
        script_id=row["script_id"],
        visual_units=units,
        created_at=row["created_at"],
    )


def _visual_unit_to_dict(unit: VisualUnit) -> dict[str, object]:
    return {
        "id": unit.id,
        "segment_refs": unit.segment_refs,
        "unit_type": unit.unit_type,
        "duration_sec": unit.duration_sec,
        "layout_template": unit.layout_template,
        "source_refs": unit.source_refs,
        "asset_refs": unit.asset_refs,
        "density_score": unit.density_score,
        "approval_state": unit.approval_state,
    }


def _dict_to_visual_unit(payload: dict[str, object]) -> VisualUnit:
    return VisualUnit(
        id=str(payload["id"]),
        segment_refs=list(payload.get("segment_refs", []) or []),
        unit_type=str(payload["unit_type"]),
        duration_sec=float(payload["duration_sec"]),
        layout_template=str(payload["layout_template"]),
        source_refs=list(payload.get("source_refs", []) or []),
        asset_refs=list(payload.get("asset_refs", []) or []),
        density_score=float(payload.get("density_score", 0.0)),
        approval_state=str(payload.get("approval_state", "auto_ok")),
    )


def _episode_plan_values(plan: EpisodePlan) -> dict[str, object]:
    return {
        "id": plan.id,
        "story_cluster_id": plan.story_cluster_id,
        "series_id": plan.series_id,
        "title_candidates": json.dumps(plan.title_candidates, ensure_ascii=False),
        "thumbnail_angles": json.dumps(plan.thumbnail_angles, ensure_ascii=False),
        "hook": plan.hook,
        "chapter_outline": json.dumps(
            [_chapter_to_dict(chapter) for chapter in plan.chapter_outline],
            ensure_ascii=False,
        ),
        "target_duration_sec": plan.target_duration_sec,
        "viewer_utility": plan.viewer_utility,
        "risk_notes": json.dumps(plan.risk_notes, ensure_ascii=False),
        "approval_state": plan.approval_state,
        "created_at": plan.created_at,
    }


def _row_to_episode_plan(row: sqlite3.Row) -> EpisodePlan:
    raw_chapters = json.loads(row["chapter_outline"] or "[]")
    chapters = [_dict_to_chapter(payload) for payload in raw_chapters]
    return EpisodePlan(
        id=row["id"],
        story_cluster_id=row["story_cluster_id"],
        series_id=row["series_id"],
        title_candidates=json.loads(row["title_candidates"] or "[]"),
        thumbnail_angles=json.loads(row["thumbnail_angles"] or "[]"),
        hook=row["hook"],
        chapter_outline=chapters,
        target_duration_sec=int(row["target_duration_sec"]),
        viewer_utility=row["viewer_utility"],
        risk_notes=json.loads(row["risk_notes"] or "[]"),
        approval_state=row["approval_state"],
        created_at=row["created_at"],
    )


def _chapter_to_dict(chapter: Chapter) -> dict[str, object]:
    return {
        "id": chapter.id,
        "title": chapter.title,
        "intent": chapter.intent,
        "target_duration_sec": chapter.target_duration_sec,
    }


def _dict_to_chapter(payload: dict[str, object]) -> Chapter:
    return Chapter(
        id=str(payload["id"]),
        title=str(payload["title"]),
        intent=str(payload["intent"]),
        target_duration_sec=int(payload["target_duration_sec"]),
    )


def _segment_to_dict(segment: ScriptSegment) -> dict[str, object]:
    return {
        "id": segment.id,
        "chapter_id": segment.chapter_id,
        "speaker": segment.speaker,
        "text": segment.text,
        "source_refs": segment.source_refs,
        "visual_refs": segment.visual_refs,
        "claim_type": segment.claim_type,
        "needs_human_review": segment.needs_human_review,
    }


def _dict_to_segment(payload: dict[str, object]) -> ScriptSegment:
    return ScriptSegment(
        id=str(payload["id"]),
        chapter_id=str(payload["chapter_id"]),
        speaker=str(payload["speaker"]),
        text=str(payload["text"]),
        source_refs=list(payload.get("source_refs", []) or []),
        visual_refs=list(payload.get("visual_refs", []) or []),
        claim_type=str(payload.get("claim_type", "interpretation")),
        needs_human_review=bool(payload.get("needs_human_review", True)),
    )


def _cluster_values(cluster: StoryCluster) -> dict[str, object]:
    return {
        "id": cluster.id,
        "title": cluster.title,
        "summary": cluster.summary,
        "primary_sources": json.dumps(cluster.primary_sources, ensure_ascii=False),
        "related_series": json.dumps(cluster.related_series, ensure_ascii=False),
        "entities": json.dumps(cluster.entities, ensure_ascii=False),
        "content_farm_overlap": cluster.content_farm_overlap,
        "cluster_date": cluster.cluster_date,
        "created_at": cluster.created_at,
        "updated_at": cluster.updated_at,
    }


def _row_to_cluster(row: sqlite3.Row, article_ids: list[str]) -> StoryCluster:
    return StoryCluster(
        id=row["id"],
        title=row["title"],
        summary=row["summary"],
        article_ids=article_ids,
        primary_sources=json.loads(row["primary_sources"] or "[]"),
        related_series=json.loads(row["related_series"] or "[]"),
        entities=json.loads(row["entities"] or "[]"),
        content_farm_overlap=float(row["content_farm_overlap"]),
        cluster_date=row["cluster_date"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _article_values(article: Article) -> dict[str, object]:
    return {
        "id": article.id,
        "url": article.url,
        "canonical_url": article.canonical_url,
        "title": article.title,
        "source_name": article.source_name,
        "source_url": article.source_url,
        "author": article.author,
        "published_at": article.published_at,
        "fetched_at": article.fetched_at,
        "body_text": article.body_text,
        "summary": article.summary,
        "language": article.language,
        "tags": json.dumps(article.tags, ensure_ascii=False),
        "source_type": article.source_type,
        "license_hint": article.license_hint,
        "hash_url": article.hash_url,
        "hash_title": article.hash_title,
        "hash_body": article.hash_body,
        "fetch_status": article.fetch_status,
        "fetch_error": article.fetch_error,
    }


def _row_to_article(row: sqlite3.Row) -> Article:
    raw_tags = row["tags"] or "[]"
    tags = json.loads(raw_tags)
    return Article(
        id=row["id"],
        url=row["url"],
        canonical_url=row["canonical_url"],
        title=row["title"],
        source_name=row["source_name"],
        source_url=row["source_url"],
        author=row["author"],
        published_at=row["published_at"],
        fetched_at=row["fetched_at"],
        body_text=row["body_text"],
        summary=row["summary"],
        language=row["language"],
        tags=tags,
        source_type=row["source_type"],
        license_hint=row["license_hint"],
        hash_url=row["hash_url"],
        hash_title=row["hash_title"],
        hash_body=row["hash_body"],
        fetch_status=row["fetch_status"],
        fetch_error=row["fetch_error"],
    )

