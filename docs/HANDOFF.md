# Handoff

Last updated: 2026-06-05

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
6. `docs/META_REVIEW_LEDGER.md` only when blocker/scope review context is needed

There is no root `AGENTS.md` in this checkout. Keep `AGENTS.md` thin if one is later added; do not turn it into roadmap, status, closeout, or history.

## Current State

- Branch: `main`
- Remote: `origin/main`
- Last pulled upstream before this active-source refresh: `13246b5 feat: add critical-view source entry path`
- Local validation on 2026-06-03 before this handoff refresh:
  - `.venv\Scripts\python.exe -m pytest -q` -> 48 passed
  - `git diff --check` -> passed
  - `.venv\Scripts\python.exe -m newsroom.cli.main export inspect --help` -> command available
- Local validation on 2026-06-04 during the meta-review / critical-source slice:
  - `.venv\Scripts\python.exe -m pytest -q` -> 53 passed.
  - `.venv\Scripts\python.exe -m newsroom.cli.main export inspect --episode-dir data\exports\episode_756343df9853` -> PASS with review warnings.
  - `git diff --check` -> passed.
- Local validation on 2026-06-05 during the active C1/NIST source application:
  - `newsroom packet add-critical` recorded C1/NIST for `story_20260603_503c39418f15862d` in `data\ymm4_import_proof.sqlite`.
  - Rebuilt packet/script/visual/asset/quote/export for `script_d2a46430e084` / `episode_756343df9853`.
  - `.venv\Scripts\python.exe -m newsroom.cli.main export inspect --episode-dir data\exports\episode_756343df9853` -> PASS; `critical_view` is no longer a warning.
  - Remaining warnings are publication/operator gates: `speculation_vs_fact`, `needs_human_review`, and 13 `human_required` visual/asset/quote items.
  - `.venv\Scripts\python.exe -m pytest -q` -> 54 passed.
  - `git diff --check` -> passed.
- Local YMM4 proof target prepared on 2026-06-03:
  - proof DB: `data\ymm4_import_proof.sqlite`
  - export bundle: `data\exports\episode_756343df9853`
  - script CSV: `data\exports\episode_756343df9853\script.csv`
  - proof draft: `data\proofs\ymm4_import\episode_756343df9853\proof.yml`
  - inspector result: `newsroom export inspect --episode-dir data\exports\episode_756343df9853` -> PASS with review warnings.
- Runtime proof artifacts under `data\proofs\` are intentionally git-ignored.
- Implementation frontier: M1 through M6.4 are implemented; a YMM4 GUI import proof target exists locally but operator GUI proof is not completed; P0-B critical-view source entry has a DB-backed CLI path and has been exercised on the active story with C1/NIST.

## Immediate Resume Packet

### P0-A: Operator-run YMM4 GUI import proof

- purpose: prove that the generated `script.csv` is accepted by real YMM4, not just by local machine checks.
- effect: upgrades the M5/M6 handoff from package-ready to YMM4-import-proven.
- requirements: an episode export bundle, `newsroom export inspect --episode-dir <episode_dir>` output, YMM4 manual import, and a filled proof YAML based on `docs/templates/ymm4_import_proof_template.yml`.
- state: local bundle generated and inspected; not operator-proven.
- owner: operator performs GUI import and records proof; assistant can inspect failures, tighten bundle checks, and update docs after proof is returned.
- next move: import `data\exports\episode_756343df9853\script.csv` in YMM4, then update `data\proofs\ymm4_import\episode_756343df9853\proof.yml` with YMM4 version, import result, checks, evidence, and decision. If this local artifact is missing, regenerate a bundle with the CLI flow below.

### P0-B: Critical-view source entry

- purpose: give operators a durable way to add or classify critical sources before packet/script review.
- effect: turns the current `critical_views` warning into an actionable workflow instead of a permanent manual reminder.
- requirements: use DB-backed source rows and `newsroom packet add-critical`; rebuild packet/script/visual/asset/quote/export artifacts after adding or classifying the source.
- state: implemented as a narrow CLI/persistence path. `story_critical_sources` records story-to-article critical views. `packet build` writes them to `sources.json` and `packet.md`; script conflict chapters prefer critical source refs; visual/asset/quote/export rebuilds use the same packet helper. The active runtime DB now records C1/NIST for `story_20260603_503c39418f15862d`; rebuilt `episode_756343df9853` no longer reports the `critical_view` warning.
- owner: assistant.
- next move: do not reselect sources unless the git-ignored runtime DB/export artifacts are missing. If regeneration is needed, reapply C1/NIST with `newsroom packet add-critical`, then rebuild downstream artifacts. Do not commit runtime DB rows.

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

## Regenerate Current Proof Target If Needed

The 2026-06-03 local target used real RSS input and selected the Microsoft Blog story `story_20260603_503c39418f15862d` / script `script_d2a46430e084` / episode `episode_756343df9853`. These runtime artifacts are git-ignored, so a different checkout may need to regenerate an equivalent target. If the exact story id is absent because RSS changed, use `shortlist --today --top 5`, choose a current official-source story, and replace the story/script/episode ids below with the ids printed by the CLI.

```powershell
.venv\Scripts\newsroom.exe --db data\ymm4_import_proof.sqlite fetch --source rss
.venv\Scripts\newsroom.exe --db data\ymm4_import_proof.sqlite cluster --days 120
.venv\Scripts\newsroom.exe --db data\ymm4_import_proof.sqlite score --today
.venv\Scripts\newsroom.exe --db data\ymm4_import_proof.sqlite shortlist --today --top 5
.venv\Scripts\newsroom.exe --db data\ymm4_import_proof.sqlite packet add-critical --story story_20260603_503c39418f15862d --url "https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence" --title "Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile" --source-name "NIST" --source-type official --note "Public risk-management framing for Microsoft official enterprise AI system narrative; adds trustworthiness, evaluation, and lifecycle risk perspective."
.venv\Scripts\newsroom.exe --db data\ymm4_import_proof.sqlite packet build --story story_20260603_503c39418f15862d
.venv\Scripts\newsroom.exe --db data\ymm4_import_proof.sqlite script draft --story story_20260603_503c39418f15862d --format anchor
.venv\Scripts\newsroom.exe --db data\ymm4_import_proof.sqlite visual plan --script script_d2a46430e084
.venv\Scripts\newsroom.exe --db data\ymm4_import_proof.sqlite asset suggest --script script_d2a46430e084
.venv\Scripts\newsroom.exe --db data\ymm4_import_proof.sqlite quote suggest --script script_d2a46430e084
.venv\Scripts\newsroom.exe --db data\ymm4_import_proof.sqlite export ymm4 --script script_d2a46430e084
.venv\Scripts\newsroom.exe --db data\ymm4_import_proof.sqlite export inspect --episode-dir data\exports\episode_756343df9853
```
