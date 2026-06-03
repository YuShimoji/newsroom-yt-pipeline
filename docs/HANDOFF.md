# Handoff

Last updated: 2026-06-03

## Restart Order

Use this order from a fresh terminal:

```powershell
git checkout main
git pull --ff-only origin main
.venv\Scripts\Activate.ps1
python -m pytest -q
git diff --check
```

If `.venv` is missing:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
```

Then read:

1. `README.md`
2. `docs/HANDOFF.md`
3. `docs/RUNTIME_STATE.md`
4. `docs/YMM4_IMPORT_PROOF.md`
5. `docs/PROJECT_SPEC.md` only when the specification boundary is needed

There is no root `AGENTS.md` in this checkout. Keep `AGENTS.md` thin if one is later added; do not turn it into roadmap, status, closeout, or history.

## Current State

- Branch: `main`
- Remote: `origin/main`
- Last pulled upstream before this handoff refresh: `8c3bc27 docs: refresh handoff restart point`
- Local validation on 2026-06-03 before this docs-only handoff refresh:
  - `.venv\Scripts\python.exe -m pytest -q` -> 48 passed
  - `git diff --check` -> passed
  - `.venv\Scripts\python.exe -m newsroom.cli.main export inspect --help` -> command available
- Implementation frontier: M1 through M6.4 are implemented; YMM4 import proof is prepared but operator GUI proof is not completed.

## Immediate Resume Packet

### P0-A: Operator-run YMM4 GUI import proof

- purpose: prove that the generated `script.csv` is accepted by real YMM4, not just by local machine checks.
- effect: upgrades the M5/M6 handoff from package-ready to YMM4-import-proven.
- requirements: an episode export bundle, `newsroom export inspect --episode-dir <episode_dir>` output, YMM4 manual import, and a filled proof YAML based on `docs/templates/ymm4_import_proof_template.yml`.
- state: prepared, not operator-proven.
- owner: operator performs GUI import and records proof; assistant can inspect failures, tighten bundle checks, and update docs after proof is returned.
- next move: choose an export bundle, run the inspector, import `<episode_dir>\script.csv` in YMM4, then save proof under `data\proofs\ymm4_import\<episode_id>\proof.yml`.

### P0-B: Critical-view source entry

- purpose: give operators a durable way to add or classify critical sources before packet/script review.
- effect: turns the current `critical_views` warning into an actionable workflow instead of a permanent manual reminder.
- requirements: decide the minimal storage surface first: packet artifact input, DB-backed source rows, or a CLI import command.
- state: not implemented.
- owner: assistant.
- next move: implement the smallest CLI and persistence path that lets a critical source survive packet, script, visual, quote, and export steps.

### P1: QuoteManifest tightening

- purpose: reduce noisy `human_required` quote rows.
- effect: review focuses on direct quote / screenshot / data-use intent instead of every source-backed segment.
- requirements: distinguish citation-only `source_refs` from direct quote or screenshot intent.
- state: not implemented.
- owner: assistant.
- next move: add intent flags or builder heuristics, then extend `tests/test_quote_manifest.py`.

### P1: Packet persistence

- purpose: store NotebookPacket records as first-class DB rows.
- effect: operator packet edits and critical-view additions survive downstream rebuilds.
- requirements: DB schema, load/upsert helpers, migration-safe existing DB behavior, and CLI readback.
- state: not implemented.
- owner: assistant.
- next move: add packet persistence after or with critical-view source entry.

## Boundaries

- NotebookLM remains a manual packet bridge; no NotebookLM API automation.
- YMM4 GUI operation is operator-owned; this repo prepares files and proof templates.
- Full `.ymmp` generation is out of scope.
- YouTube upload and publishing are out of scope.
- Inoreader OAuth/token flow is deferred.
- External image download and automatic external asset approval remain out of scope.
- NLMYTGen integration is schema-only: CSV / JSON / Markdown handoff, not subprocess, path dependency, pip dependency, or shared code.

## Proof And Artifact Locations

- Runtime state: `docs/RUNTIME_STATE.md`
- YMM4 proof procedure: `docs/YMM4_IMPORT_PROOF.md`
- Proof template: `docs/templates/ymm4_import_proof_template.yml`
- Standard export bundles: `data\exports\episode_<id>\`
- Recommended runtime proof path: `data\proofs\ymm4_import\<episode_id>\proof.yml`

