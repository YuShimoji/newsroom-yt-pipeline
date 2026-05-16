from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from newsroom.store.models import Article


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


def count_articles(db_path: str | Path) -> int:
    init_db(db_path)
    with connect(db_path) as connection:
        row = connection.execute("SELECT COUNT(*) AS count FROM articles").fetchone()
    return int(row["count"])


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

