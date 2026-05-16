# newsroom-yt-pipeline

`newsroom-yt-pipeline` is a semi-automated article ledger and editorial pipeline for a network-news-focused YouTube channel.

The M1 scope is intentionally narrow: collect RSS articles, store them in SQLite, deduplicate them, and print a daily candidate report. Video generation, NotebookLM automation, YMM4 export, asset downloading, YouTube upload, GUI work, and full `.ymmp` generation are not part of M1.

## Current Milestone: M1 Article Ledger

Implemented in M1:

- Python package scaffold.
- Config files under `configs/`.
- `Article` and `SourceFeed` models.
- SQLite persistence.
- RSS feed parsing and fetching.
- Inoreader client stub.
- `newsroom fetch --source rss`.
- `newsroom report --today`.
- Focused tests for config load, RSS normalization, DB deduplication, and report output.

## Install

```bash
python -m pip install -e .[dev]
```

## Usage

Fetch enabled RSS feeds from `configs/sources.yml`:

```bash
newsroom fetch --source rss
```

Print today's stored article candidates:

```bash
newsroom report --today
```

Use a custom database path:

```bash
newsroom fetch --source rss --db data/newsroom.sqlite
newsroom report --today --db data/newsroom.sqlite
```

## Architecture Boundary

This repository owns source ingest, article ledger, story clustering, scoring, NotebookLM packet preparation, script workbench interfaces, visual planning interfaces, and rights manifests.

`NLMYTGen` remains a downstream adapter for NotebookLM/YMM4 conversion. News ingestion, source strategy, rights management, channel planning, and publishing decisions should not be moved into `NLMYTGen`.

## Non-Scope For M1

- NotebookLM API automation.
- YMM4 export.
- Asset download or automatic media use.
- YouTube upload/publishing.
- GUI/dashboard.
- Full `.ymmp` generation.
- Final script generation.

## Next Milestones

- M2: story clustering and topic scoring.
- M3: NotebookLM packet builder.
- M4: script workbench.
- M5: YMM4 export through a `NLMYTGen` adapter.
- M6: VisualIR, AssetManifest, and QuoteManifest.
- M7: series planner and channel memory.

