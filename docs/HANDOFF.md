# Handoff

Last updated: 2026-06-07

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
- YMM4 GUI proof attempt on 2026-06-05:
  - YMM4 version: `4.43.1.0`.
  - target CSV: `data\exports\episode_756343df9853\script.csv`.
  - result: not passed. YMM4 opened `台本編集 / script.csv`, then showed `キャラクターが見つかりませんでした。キャラクターを指定してください。`
  - cause to resolve: exported speaker is `ナレーター`, but the local YMM4 character setup did not contain a matching `ナレーター` character and showed `ゆっくり霊夢` instead.
  - ignored proof record: `data\proofs\ymm4_import\episode_756343df9853\proof.yml` was updated locally with `import_result: failed` / `decision.status: needs_fix`.
- Local validation before this handoff push:
  - `.venv\Scripts\python.exe -m pytest -q` -> 54 passed.
  - `git diff --check` -> passed.
  - `.venv\Scripts\python.exe -m newsroom.cli.main export inspect --episode-dir data\exports\episode_756343df9853` -> PASS in this checkout, but the git-ignored export bundle still showed the older `critical_view` warning. If this matters for the next run, regenerate the active C1/NIST runtime artifacts with the commands below.
- P0-A context reflection:
  - Subtitle placement authority remains downstream in NLMYTGen/YMM4-side tooling.
  - The newsroom-side YMM4 proof scope is CSV import acceptance and handoff-file readability only.
  - Git-ignored runtime export/proof state is checkout-sensitive. A refreshed active C1/NIST bundle should inspect PASS with no `critical_view` warning; if a checkout still shows the older warning, regenerate the active C1/NIST runtime artifacts with the commands below.
- P0-A request validity check on 2026-06-06:
  - The request is valid as an operator-environment follow-up, not as a newsroom code or speaker-mapping change.
  - The local proof record reports YMM4 `4.43.1.0` and `needs_fix` because speaker `ナレーター` was missing from the YMM4 character registry.
  - A filesystem read under `C:\Users\thank\AppData\Local\YukkuriMovieMaker\v4` found only `temp` content, so there is no identified safe file-backed registry to edit directly from this repo run.
  - Do not change `configs\speakers.yml` to `ゆっくり霊夢` merely to satisfy the local GUI. Prepare a `ナレーター` character in YMM4, or make an explicit editorial decision to export a different speaker name, then rerun the proof.
- P0-A YMM4 GUI proof pass on 2026-06-07:
  - Operator created a YMM4 character named `ナレーター` as an emergency speaker binding fix.
  - YMM4 recognized and imported `data\exports\episode_756343df9853\script.csv` normally.
  - `TODO[...]` tokens were pronounced because they are literal skeleton script text, not an import failure.
  - Local proof record `data\proofs\ymm4_import\episode_756343df9853\proof.yml` was updated to `import_result: pass` / `decision.status: passed`.
  - This proves CSV import acceptance and handoff-file readability only; subtitle placement, overlay safety, and final YMM4 geometry remain downstream scope.
- Post-proof TODO skeleton gate on 2026-06-07:
  - Active `script.csv` / `script_ir.json` still contain literal `TODO[...]` text in all 6 spoken rows.
  - `export inspect` now reports this as `script_todo_skeleton` warning while keeping the bundle PASS.
  - P0.5 Script materialization / TODO skeleton replacement should run before P1 QuoteManifest tightening.
- P0.5 materialization draft path on 2026-06-07:
  - Added `newsroom script materialize --script <script_id>`.
  - The command writes `data\scripts\<script_id>\script_materialization.yml` with segment ids, speaker, current TODO text, source refs, critical refs, suggested operator angle, empty `operator_fill`, and human-review state.
  - It does not replace `script_ir.json`, `script.csv`, DB rows, or export bundles. `script_todo_skeleton` remains until operator-approved replacement updates the spoken text.
- P0.5-B operator-approved replacement intake on 2026-06-07:
  - Added `newsroom script apply-materialization --script <script_id> --draft <path> --require-approved`.
  - The command rejects empty `operator_fill`, `replacement_status` other than `approved`, stale `current_text`, speaker mismatches, and source/critical ref mismatches.
  - Successful apply updates the DB ScriptIR text and refreshed `data\scripts\<script_id>\` bundle only; export bundles are not rebuilt automatically.
  - Active `data\scripts\script_d2a46430e084\script_materialization.yml` is still unfilled/unapproved, so active replacement was not executed.
- Approved narration authority decision on 2026-06-07:
  - `script_materialization.yml`, DB ScriptIR rows, and export bundles are runtime artifacts and are not portable production authority across checkouts.
  - This lane may use local runtime replacement as proof only after operator-approved text exists, but durable approved narration authority is deferred to Script/Packet persistence.
  - Do not commit the ignored runtime draft/export as the canonical script, and do not treat runtime-only replacement as reproducible project state.
- Local validation after the P0.5-B replacement intake slice:
  - `.venv\Scripts\python.exe -m pytest tests\test_script_materialization.py tests\test_export_inspector.py -q` -> 16 passed.
  - `.venv\Scripts\python.exe -m pytest -q` -> 64 passed.
  - `git diff --check` -> passed.
  - Active apply command rejected the unfilled/unapproved runtime draft as expected; DB ScriptIR and export bundle still have 6 / 6 TODO rows.
  - `.venv\Scripts\python.exe -m newsroom.cli.main export inspect --episode-dir data\exports\episode_756343df9853` -> PASS with `script_todo_skeleton` still present and `critical_view` absent.
- Local validation after the P0.5 materialization draft slice:
  - `.venv\Scripts\python.exe -m pytest tests\test_script_materialization.py tests\test_export_inspector.py -q` -> 10 passed.
  - `.venv\Scripts\python.exe -m pytest -q` -> 58 passed.
  - `git diff --check` -> passed.
  - `.venv\Scripts\python.exe -m newsroom.cli.main --db data\ymm4_import_proof.sqlite script materialize --script script_d2a46430e084` -> wrote ignored `data\scripts\script_d2a46430e084\script_materialization.yml`.
  - `.venv\Scripts\python.exe -m newsroom.cli.main export inspect --episode-dir data\exports\episode_756343df9853` -> PASS with `script_todo_skeleton` still present and `critical_view` absent.
- Local validation after the TODO skeleton inspector slice:
  - `.venv\Scripts\python.exe -m pytest -q` -> 55 passed.
  - `git diff --check` -> passed.
  - `.venv\Scripts\python.exe -m newsroom.cli.main export inspect --episode-dir data\exports\episode_756343df9853` -> PASS with `script_todo_skeleton`, `speculation_vs_fact`, `needs_human_review`, and `human_required` warnings; `critical_view` warning remains absent.
- Local YMM4 proof target prepared on 2026-06-03:
  - proof DB: `data\ymm4_import_proof.sqlite`
  - export bundle: `data\exports\episode_756343df9853`
  - script CSV: `data\exports\episode_756343df9853\script.csv`
  - proof draft: `data\proofs\ymm4_import\episode_756343df9853\proof.yml`
  - inspector result: `newsroom export inspect --episode-dir data\exports\episode_756343df9853` -> PASS with review warnings.
- Runtime proof artifacts under `data\proofs\` are intentionally git-ignored.
- Implementation frontier: M1 through M6.4 are implemented; P0-A CSV import acceptance is proven for the active YMM4 export after adding the `ナレーター` character in the target YMM4 environment; P0-B critical-view source entry has a DB-backed CLI path and has been exercised on the active story with C1/NIST; P0.5 draft and reject-first apply paths are implemented, but the active draft still needs operator fill/approval before TODO spoken rows can be cleared.

## Immediate Resume Packet

### P0-A: Operator-run YMM4 GUI import proof

- purpose: prove that the generated `script.csv` is accepted by real YMM4, not just by local machine checks.
- effect: upgrades the M5/M6 handoff from package-ready to YMM4-import-proven.
- requirements: an episode export bundle, `newsroom export inspect --episode-dir <episode_dir>` output, YMM4 manual import, and a filled proof YAML based on `docs/templates/ymm4_import_proof_template.yml`.
- state: passed on 2026-06-07 after the operator created a YMM4 character named `ナレーター`; `script.csv` was recognized and imported normally.
- scope: CSV import acceptance and handoff-file readability only. This is not subtitle layout, subtitle position, overlay safety, or final YMM4 geometry proof.
- owner: operator owns any further YMM4 GUI review; assistant owns tracked docs/code updates when returned proof changes repo state.
- next move: continue with publication/operator review gates and the next assistant-owned backlog item. Do not treat this as subtitle layout, overlay safety, or final geometry proof.

### P0-B: Critical-view source entry

- purpose: give operators a durable way to add or classify critical sources before packet/script review.
- effect: turns the current `critical_views` warning into an actionable workflow instead of a permanent manual reminder.
- requirements: use DB-backed source rows and `newsroom packet add-critical`; rebuild packet/script/visual/asset/quote/export artifacts after adding or classifying the source.
- state: implemented as a narrow CLI/persistence path. `story_critical_sources` records story-to-article critical views. `packet build` writes them to `sources.json` and `packet.md`; script conflict chapters prefer critical source refs; visual/asset/quote/export rebuilds use the same packet helper. The active runtime DB now records C1/NIST for `story_20260603_503c39418f15862d`; rebuilt `episode_756343df9853` no longer reports the `critical_view` warning.
- owner: assistant.
- next move: do not reselect sources unless the git-ignored runtime DB/export artifacts are missing. If regeneration is needed, reapply C1/NIST with `newsroom packet add-critical`, then rebuild downstream artifacts. Do not commit runtime DB rows.

### P0.5: Script materialization / TODO skeleton replacement

- purpose: replace literal `TODO[...]` spoken rows with reviewable narration for the active script.
- effect: moves the active export from YMM4-importable skeleton to production-reviewable script content.
- requirements: preserve speaker `ナレーター`, CSV import shape, existing `source_refs`, C1/NIST critical-view coverage, and human-review flags unless the reviewer explicitly clears them.
- state: draft path and reject-first apply path implemented. `newsroom script materialize --script script_d2a46430e084` writes `data\scripts\script_d2a46430e084\script_materialization.yml`; `newsroom script apply-materialization --script script_d2a46430e084 --draft data\scripts\script_d2a46430e084\script_materialization.yml --require-approved` rejects the active draft because all 6 `operator_fill` values are empty and all rows remain `operator_pending`. Active `script.csv` / `script_ir.json` still have 6 / 6 TODO skeleton spoken rows, and `export inspect` reports `script_todo_skeleton` as a warning.
- authority: approved narration is not durable yet. A local apply can prove replacement mechanics, but another checkout cannot reproduce approved narration from ignored runtime DB/export/draft artifacts until Script/Packet persistence defines the canonical storage path.
- owner: assistant for tooling/rebuilds and operator for editorial approval of final narration.
- next move: operator fills and approves `operator_fill` values. Then either run a clearly labeled runtime-only apply/export proof, or implement durable Script/Packet persistence before treating the approved narration as portable project authority. Do not proceed to QuoteManifest tightening as the active path while the script is still TODO skeleton.

### P1: QuoteManifest tightening

- purpose: reduce noisy `human_required` quote rows.
- effect: review focuses on direct quote / screenshot / data-use intent instead of every source-backed segment.
- requirements: distinguish citation-only `source_refs` from direct quote or screenshot intent.
- state: not implemented.
- owner: assistant.
- next move: after P0.5 materializes the active script, add intent flags or builder heuristics, then extend `tests/test_quote_manifest.py`.

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
- Newsroom YMM4 proof is limited to CSV import acceptance and handoff-file readability; subtitle placement authority, YMM4 item geometry, template positioning, subtitle band decisions, `.ymmp` patch details, and overlay proof belong downstream.
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
