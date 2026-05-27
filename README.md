# newsroom-yt-pipeline

`newsroom-yt-pipeline` is a semi-automated article ledger and editorial pipeline for a network-news-focused YouTube channel.

The current implementation state is tracked in [`docs/RUNTIME_STATE.md`](docs/RUNTIME_STATE.md). That file is the first stop for restart status, validation proof, implemented milestones, and the next recommended slice.

## Initial MVP: M1 Article Ledger

M1 was intentionally narrow: collect RSS articles, store them in SQLite, deduplicate them, and print a daily candidate report. Later milestones now exist in code, so this section is retained as initial MVP context rather than the current project frontier.

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

A virtual environment is recommended to avoid polluting the system Python and to keep dev extras isolated.

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1      # PowerShell on Windows
# source .venv/bin/activate     # POSIX shells
python -m pip install -e .[dev]
```

The `newsroom` CLI is exposed on PATH inside the activated venv.

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

## Tests

Focused tests cover config load, RSS normalization, DB deduplication, and report output. Run them when verifying a change; they are not intended to be wired into a continuous loop.

```bash
python -m pytest -q
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
