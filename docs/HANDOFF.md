# Handoff

Last updated: 2026-06-22

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

1. `AGENTS.md`
2. `README.md`
3. `docs/HANDOFF.md`
4. `docs/RUNTIME_STATE.md`
5. `docs/DEVELOPMENT_PRACTICES.md`
6. `artifacts/ARTIFACTS.md` when reviewable artifacts are involved
7. `docs/YMM4_IMPORT_PROOF.md` when YMM4 proof state is involved
8. `docs/PROJECT_SPEC.md` only when the specification boundary is needed
9. `docs/META_REVIEW_LEDGER.md` only when blocker/scope review context is needed

Root `AGENTS.md` is a thin pointer into the restart docs. Do not turn it into roadmap, status, closeout, or history.

## Review And Autonomy Contract

- Review input from the user is freeform. Do not ask for fixed phrases such as `accept`, `reject`, or `small_adjustment`; interpret natural feedback internally by target, intent, constraints, and confidence.
- When review is needed, place a Review Card beside the artifact access details with the target, up to three checkpoints, freeform examples, and the agent's planned handling. If review is useful but not blocking, record Review Debt and keep moving.
- Operation Cockpit v1.11 closeouts should include a Routing Header, Current State, Completion Matrix, expected-vs-actual result, changed files or `none`, artifact identity/access, Review Card / Review Debt, Action Ledger, User-Side Work, Agent-Side Work, Goal Stack, Turn Calendar, Decision Packet, Metric Change Note when needed, and Continuation State.
- Completion Matrix rows must expose `done`, `total`, `unknown`, `missing`, and an `ASCII_SAFE` meter. Use `#` and `-` only, such as `[#####-] 5/6` or `[########--] 14/18`; do not use Unicode block/shaded characters, emoji meters, full-width block meters, or decorative glyph meters in chat reports.
- Supervisor Relay is slice-specific. Do not include a next-Agent prompt in normal reports unless the Handoff Gate is true and the report names purpose, effect, requirements, state, owner, and next move.
- In long-run autonomy, continue through the next one to three scoped, reversible actions when no true stop condition is present. Do not convert missing optional review into a stop unless the wrong interpretation would materially change artifact direction.

## Current State

- Branch: `main`
- Remote: `origin/main`
- Cross-terminal context sync on 2026-06-22:
  - User requested preserving all current project context in tracked project files and reflecting local state to `origin/main` for immediate restart from another terminal.
  - Pre-edit sync check: `git fetch --prune origin` completed, `HEAD...origin/main = 0 0`, and the worktree was clean at `912ce3b feat: validate NLMYTGen export fixture`.
  - Latest pushed implementation baseline before this handoff refresh is the NLMYTGen fake export fixture contract/readback slice. The active reference artifact remains `newsroom-export-fixture-for-nlmytgen` in `artifacts/ARTIFACTS.md`.
  - Local ignored runtime artifacts are present in this checkout under `data\` and `.mkdocs-site\`; they are evidence only and are not part of the push. Current local `export inspect --episode-dir data\exports\episode_756343df9853` read back PASS / `No issues found.`
  - `series report --series copilot_watch` read back one active episode, Microsoft Blog as `vendor_official / microsoft_official / official`, NIST as `standards_body / standards_body / official`, and follow-up seeds still marked as seeds, not approved stories.
  - Validation for this handoff refresh: fixture test passed with 5 tests; full `.venv\Scripts\python.exe -m pytest -q` passed with 121 tests; `git diff --check` passed; `.venv\Scripts\python.exe -m mkdocs build --strict` passed with the existing Material for MkDocs upstream warning only; conflict-marker scan returned no matches.
  - Next terminal should `git pull --ff-only origin main`, read `AGENTS.md`, this file, `docs\RUNTIME_STATE.md`, `docs\DEVELOPMENT_PRACTICES.md`, and `artifacts\ARTIFACTS.md`, then rerun local validation before choosing one scoped lane.
- v1.11 cockpit / stable-meter alignment on 2026-06-20:
  - `git fetch --prune origin` showed `origin/main` advanced from `3235175` to `7460ee6`; `git pull --ff-only origin main` fast-forwarded this checkout to `7460ee6 docs: refresh 2026-06-19 sync handoff`.
  - Verified `main`, `HEAD...origin/main = 0 0`, and a clean worktree before scoped docs edits.
  - Active reference artifact is `newsroom-cockpit-governance` in `artifacts/ARTIFACTS.md`; source-of-truth guidance is in `docs/DEVELOPMENT_PRACTICES.md`, with continuation state in `docs/RUNTIME_STATE.md`.
  - Scope is docs/report governance plus docs-view dependency reproducibility: Routing Header, Completion Matrix, `ASCII_SAFE` meters, Turn Calendar, Report Mode, Supervisor Relay, artifact identity/access, Handoff Gate behavior, and `mkdocs-material` in the `dev` extra.
  - Validation for this alignment: `.venv\Scripts\python.exe -m pytest -q` -> 116 passed; `git diff --check` -> passed; `.venv\Scripts\python.exe -m mkdocs build --strict` -> passed; `scripts\operator\open_dashboard.ps1 -Port 8011 -NoBrowser` -> exited 0 and the temporary server was not left running; synthetic `packet critical-list --format json` smoke returned one critical-view row with no URL field; non-ASCII chat/report meter search returned no matches.
- Cross-terminal context sync on 2026-06-19:
  - User explicitly requested preserving all current project context and reflecting local state to `origin/main` for immediate restart from another terminal.
  - `git fetch --prune origin` showed `origin/main` had advanced from `ed35d9d` to `3235175`; local `main` was behind by 2 commits with no divergence.
  - Fast-forwarded with `git pull --ff-only origin main` to `3235175 docs: refresh remote handoff context`, which includes `bce6a31 feat: read back critical source notes` and the tracked root `AGENTS.md` handoff entry point.
  - Validation before this handoff refresh commit: `python -m pytest -q` -> 116 passed; `git diff --check` -> passed; `python -m mkdocs build --strict` -> passed after stopping a stale local MkDocs server; synthetic `packet critical-list --format json` smoke returned one critical-view row with note/readback and no URL field; `scripts\operator\open_dashboard.ps1 -NoBrowser` exited 0.
  - This handoff refresh records the 2026-06-19 sync state before pushing; after pulling it, a fresh terminal should read `AGENTS.md`, `docs\HANDOFF.md`, `docs\RUNTIME_STATE.md`, `docs\DEVELOPMENT_PRACTICES.md`, and `artifacts\ARTIFACTS.md`, then rerun local validation before choosing one scoped lane.
- Cross-terminal context sync on 2026-06-18:
  - Started from `main` / `origin/main` parity at `bce6a31 feat: read back critical source notes`; `HEAD...origin/main = 0 0`; the only local dirty item was thin untracked `AGENTS.md`.
  - Added root `AGENTS.md` as a tracked, minimal entry point and refreshed `docs/HANDOFF.md` / `docs/RUNTIME_STATE.md` so another terminal can resume from project files instead of chat context.
  - Recovery commit `bce6a31` is the current implementation baseline on remote and makes `packet critical-list` read back `note` and `recorded_at` without exposing source URLs.
  - Backup branch `backup/local-main-641e14e-before-ed35d9d-sync` preserves the stale divergent local branch at `641e14e`; it is evidence only and must not be merged into `main` unless a future audit explicitly asks for it.
  - Validation for this context sync: `python -m pytest -q` passed with 116 tests; `git diff --check` passed; synthetic `packet critical-list --format json` smoke returned one critical-view row with `url_field_present=false`; MkDocs strict build was unavailable because `.venv` does not currently have `mkdocs`.
- Remote sync handoff on 2026-06-17:
  - User explicitly requested preserving all project context and reflecting local state to `origin/main` so another terminal can resume immediately.
  - Pre-sync verification after `git fetch --prune origin`: `main` at `1e331fc docs: align freeform review autonomy contract`, `HEAD...origin/main = 2 0`, and the worktree was clean.
  - Local commits being synced: `00cd5d3 docs: add operation cockpit access launcher`, `1e331fc docs: align freeform review autonomy contract`, and this handoff refresh commit.
  - Validation before this handoff refresh commit: `python -m pytest -q` -> 116 passed; `git diff --check` -> passed; `python -m mkdocs build --strict` -> passed; synthetic `packet critical-list --format json` smoke returned one critical-view row with no URL field; `scripts\operator\open_dashboard.ps1 -NoBrowser` exited 0.
  - After pulling this sync, a fresh terminal should read `docs\HANDOFF.md`, `docs\RUNTIME_STATE.md`, `docs\DEVELOPMENT_PRACTICES.md`, and `artifacts\ARTIFACTS.md`, then rerun local validation before choosing the next scoped lane.
- v1.8 Freeform Review / Long-Run Autonomy alignment on 2026-06-17:
  - Verified this checkout on `main` at `00cd5d3 docs: add operation cockpit access launcher`, with `HEAD...origin/main = 1 0` and a clean worktree before the alignment edits.
  - Push was initially deferred because the v1.8 slice did not explicitly approve pushing the local-ahead commit; the later remote-sync request on 2026-06-17 supersedes that deferral.
  - The active documentation target is the Operation Cockpit / review-access contract, not a broad feature lane such as QuoteManifest tightening.
  - Validation passed for the local alignment: full pytest, whitespace diff check, MkDocs strict build, synthetic `packet critical-list --format json` smoke, and docs launcher smoke.
- Remote sync handoff on 2026-06-15:
  - Started clean on `main` at `14c1e4f feat: tighten quote manifest review levels` with `HEAD...origin/main = 4 0`.
  - Local commits being handed off: `baabcd6 docs: add development practice docs view`, `d7f2bd7 feat: add critical source readback`, `d90452a docs: record review artifact contract`, and `14c1e4f feat: tighten quote manifest review levels`.
  - This handoff update keeps the restart context in tracked docs before pushing to `origin/main`; after sync, another terminal should `git pull --ff-only origin main`, read this file and `docs\RUNTIME_STATE.md`, then run local validation.
  - Latest validation before sync: `.venv\Scripts\python.exe -m pytest -q` -> 116 passed; `git diff --check` -> passed; `.venv\Scripts\python.exe -m mkdocs build --strict` -> passed; synthetic `packet critical-list --format json` smoke returned one critical view and no URL field.
  - The remote sync does not include runtime DBs, generated export bundles, proof screenshots, YMM4 geometry, `.ymmp` files, NotebookLM/YMM4 automation, YouTube publishing, or raw source bodies.
- Newsroom handoff inventory record on 2026-06-10:
  - Recorded the read-only inventory of active export `data\exports\episode_756343df9853` in `docs\verification\NEWSROOM-HANDOFF-INVENTORY-2026-06-10.md`.
  - The export folder exists with 9 handoff files: manifest, script CSV/IR, source list, visual plan/IR, asset manifest, quote manifest, and YMM4 notes.
  - `newsroom series report --series copilot_watch` reads back Microsoft Blog as `vendor_official / microsoft_official / official` and NIST as `standards_body / standards_body / official`; `unclassified / no_pool` is absent.
  - `newsroom export inspect --episode-dir data\exports\episode_756343df9853` returns PASS / `No issues found.`
  - Handoff readiness remains `partial`: the package is a Newsroom-side candidate for NLMYTGen review, but copy-in authority, read-only path authority, source/rights/production approval, YMM4 geometry, subtitle placement, overlay proof, `.ymmp`, render, and publishing authority are not supplied.
  - No NLMYTGen repo change, copy-in, read-only path pinning, runtime export/proof/DB commit, source adoption, seed promotion, NotebookLM automation, Inoreader OAuth, broad crawling, render, production, or publishing work was performed.
  - Next action requires an explicit human decision: copy the package into NLMYTGen, review it by read-only path, or keep the handoff on hold.
- Cross-terminal no-op restart check on 2026-06-09:
  - Started from `1296b8e docs: backfill channel memory source roles`.
  - `git checkout main` and `git pull --ff-only origin main` confirmed `Already up to date`.
  - `HEAD...origin/main`: `0 0`
  - Working tree: clean; `git status --porcelain=v1 --untracked-files=all` returned no files.
  - Channel-memory validation: `.venv\Scripts\python.exe -m pytest tests\test_channel_memory.py -q` -> 16 passed.
  - Active series report: `newsroom series report --series copilot_watch` reads back Microsoft Blog as `vendor_official / microsoft_official / official` and NIST as `standards_body / standards_body / official`; `unclassified / no_pool` is absent.
  - Follow-up candidates remain `seed` and are not approved stories: `copilot_governance_controls`, `copilot_user_value_gap`.
  - Active export inspect: `.venv\Scripts\python.exe -m newsroom.cli.main export inspect --episode-dir data\exports\episode_756343df9853` -> PASS / `No issues found.`
  - `git diff --check` passed.
  - No M7-D reimplementation, seed promotion, source adoption, broad crawling, NotebookLM/YMM4 automation, runtime artifact commit, or downstream subtitle/YMM4 geometry work.
  - Next action still requires one explicit human input: an approved second episode record YAML full path, a selected follow-up seed, or a concrete downstream failure log/artifact/proof path.
- Cross-terminal handoff confirmation after M7-D on 2026-06-08:
  - Synced start commit before M7-D local changes: `ad81fd2 docs: refresh M7-C handoff`
  - `HEAD...origin/main`: `0 0`
  - Working tree: clean
  - Full validation: `.venv\Scripts\python.exe -m pytest -q` -> 107 passed.
  - Channel-memory validation: `.venv\Scripts\python.exe -m pytest tests\test_channel_memory.py -q` -> 16 passed.
  - Active series report: `newsroom series report --series copilot_watch` reads back Microsoft Blog as `vendor_official / microsoft_official` and NIST as `standards_body / standards_body`; `unclassified / no_pool` is absent.
  - Active export inspect: PASS / `No issues found.`
  - Next assistant-owned backlog item: wait for an operator-approved second episode record, an explicit follow-up seed selection, or a concrete downstream failure.
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
- P0.5-C approved materialization authority on 2026-06-07:
  - Added tracked sanitized approved-materialization record support under `docs\approved_materializations\`.
  - Added `newsroom script approve-materialization` to validate a filled/approved runtime draft and write `docs\approved_materializations\<script_id>.materialization.yml`.
  - Added `newsroom script apply-approved-materialization` to apply a tracked record to DB ScriptIR and the refreshed script bundle while preserving speaker, source refs, critical refs, visual refs, claim type, and review flags.
  - Approved records exclude source catalogs, raw article body, private data, runtime DB paths, screenshots, YMM4 geometry, subtitle coordinates, `.ymmp` details, and overlay proof.
  - Active `data\scripts\script_d2a46430e084\script_materialization.yml` is still unfilled/unapproved, so no active approved record was generated and no active replacement was executed.
- P0.5-D approved materialization apply on 2026-06-07:
  - Operator explicitly approved adopting all 6 `operator_fill_suggestion` values from `data\scripts\script_d2a46430e084\script_materialization.yml` as narration.
  - The ignored runtime draft was filled locally with those exact suggestion values and all 6 segment `replacement_status` values were set to `approved`.
  - Generated tracked sanitized authority record: `docs\approved_materializations\script_d2a46430e084.materialization.yml`.
  - Applied the approved record to DB ScriptIR and refreshed `data\scripts\script_d2a46430e084\` while preserving `ナレーター`, source refs, C1/NIST critical refs, visual refs, claim type, and human-review flags.
  - Rebuilt `data\exports\episode_756343df9853`; `export inspect` now passes with `script_todo_skeleton` absent and `critical_view` absent.
- P1 remaining visual/asset/screenshot gate on 2026-06-07:
  - The remaining 1 visual, 1 asset, and 1 quote `human_required` items were all traced to the facts chapter's default `source_card` screenshot intent.
  - Classification decision: `replace_with_local_diagram` for the active export because the script uses citation-only source refs and does not require an external screenshot.
  - `source_card` still means explicit screenshot/source-display intent and remains `human_required`; citation-only facts now default to `claim_evidence_card`.
  - Rebuilt VisualIR/AssetManifest/QuoteManifest/export for `script_d2a46430e084`; the active export now has 0 visual/asset/quote `human_required` items while preserving source refs and C1/NIST citation rows.
  - `export inspect` now passes with `critical_view` absent, `script_todo_skeleton` absent, and only `speculation_vs_fact` plus 6 broad `needs_human_review` warnings.
- P1 broad script review gate on 2026-06-07:
  - Added tracked review handoff artifact: `docs\script_review_gates\script_d2a46430e084.review.yml`.
  - Classification decision: no script text adjustment was made. All 6 segments remain `operator_approval_required`; interpretation rows also keep `speculation_vs_fact` / publication-review caution until operator approval or requested wording changes.
  - The approved narration authority remains `docs\approved_materializations\script_d2a46430e084.materialization.yml`; the review gate artifact is not a replacement authority.
  - Active export remains PASS with `critical_view`, `script_todo_skeleton`, and visual/asset/quote `human_required` absent.
  - Remaining warnings intentionally stay: `speculation_vs_fact` and 6 broad `needs_human_review` segment warnings.
- P1 operator script review decision apply path on 2026-06-07:
  - Operator/editorial decision approved all 6 revised segments as source-bounded narration within the Microsoft official narrative and NIST risk framing.
  - Updated `docs\approved_materializations\script_d2a46430e084.materialization.yml` with the approved facts/takeaway minor edits, the approved intro/context/conflict/impact text, and `human_review_required: false` for all 6 segments.
  - Updated `docs\script_review_gates\script_d2a46430e084.review.yml` to `status: operator_review_applied`; `needs_human_review` is `cleared_by_operator` and `speculation_vs_fact` is `cleared_by_operator_decision`.
  - `newsroom script apply-approved-materialization` now supports reapplying a tracked approved record to already-materialized ScriptIR rows and can apply the approved `human_review_required` flag while still validating speaker, source refs, critical refs, visual refs, and claim type.
  - Reapplied the approved record, rebuilt VisualIR/AssetManifest/QuoteManifest/export for `script_d2a46430e084`, and confirmed `export inspect` -> PASS with no issues found.
  - This is not publishing approval, legal approval, YMM4 visual approval, subtitle placement proof, overlay safety proof, or final YMM4 geometry proof.
- P1 Packet persistence on 2026-06-07:
  - Added `notebook_packets` as a first-class DB table for sanitized NotebookPacket records: source refs, timeline, glossary, questions, format hint, export dir, and timestamps.
  - Added `upsert_notebook_packet`, `load_notebook_packet`, and `load_notebook_packet_for_story`.
  - `newsroom packet build` now persists the packet before writing packet artifacts, and `newsroom packet show --packet <id>` / `--story <story_id>` reads persisted packet state back from the runtime DB.
  - Downstream packet helper now prefers a persisted packet when present, preserving operator-edited questions/glossary/source choices, while appending newly required critical-view refs from `story_critical_sources` so C1/NIST additions are not lost.
  - Runtime DB/export artifacts remain local and are not committed.
- P2 Source expansion gate on 2026-06-08:
  - Added `configs\source_pools.yml` as a deliberate source-pool registry with the allowed roles `vendor_official`, `regulator_public`, `standards_body`, `independent_analysis`, `technical_reference`, and `critical_view_candidate`.
  - Existing RSS feed entries now carry `source_pool_id`; feed loading applies pool defaults as metadata only.
  - RSS-ingested articles and packet `SourceRef` rows can carry `source_role` / `source_pool_id`; persisted packet JSON keeps that metadata.
  - `critical_view_candidate` sources are exposed as candidates and are not auto-adopted into `packet.critical_views`; explicit operator/manual critical selection still works.
  - No broad crawling, Inoreader OAuth/token flow, NotebookLM API automation, source scraping, or automatic source adoption was added.
  - Validation: targeted source/storage/packet tests -> 16 passed; full `.venv\Scripts\python.exe -m pytest -q` -> 91 passed; `git diff --check` -> passed; active `packet show --story story_20260603_503c39418f15862d` and `export inspect --episode-dir data\exports\episode_756343df9853` still pass.
- M7 channel memory seed on 2026-06-08:
  - Added `docs\channel_memory\copilot_watch.yml` as a tracked sanitized memory record for the active Copilot Watch episode.
  - Added `newsroom.editorial.channel_memory` as a small YAML loader/validator for series memory, episode ids, source-role coverage, critical-view use, compact claim summaries, open questions, and follow-up seeds.
  - The record references `episode_756343df9853`, `story_20260603_503c39418f15862d`, `script_d2a46430e084`, `packet_20260603_2de578dcd4b0`, the approved materialization record, and the script review gate without copying approved narration text.
  - Channel memory records reject raw article body, private data, full approved text, runtime DB paths, screenshots, YMM4 geometry, subtitle coordinates, `.ymmp`, and overlay proof fields.
  - This is not autonomous topic recommendation, broad crawling, NotebookLM automation, NLMYTGen integration, publishing strategy, or a dashboard.
  - Validation: channel-memory tests -> 5 passed; active export inspect remained PASS / `No issues found.`
- M7-B series report / channel memory readback on 2026-06-08:
  - Added `newsroom series report --series <series_id>` to render tracked channel memory for human review.
  - The report shows series title/status, episode count, episode/story/script/packet ids, source-role coverage, critical views, compact claims, open questions, and follow-up seeds.
  - The report explicitly states that follow-up seeds are not approved stories and still require normal editorial selection and source approval.
  - No episode append workflow, autonomous recommendation, source candidate promotion, dashboard, publishing strategy, NLMYTGen integration, DB migration, or runtime export mutation was added.
  - Validation: channel-memory CLI tests -> 7 passed; full `.venv\Scripts\python.exe -m pytest -q` -> 98 passed; `git diff --check` -> passed; active export inspect remained PASS / `No issues found.`
- M7-C channel memory append workflow on 2026-06-08:
  - Added `newsroom series append-episode --series <series_id> --episode-record <path>` as a file-based append path for already approved episode memory.
  - The append path validates the existing tracked memory and incoming episode record, rejects duplicate `episode_id`, `story_id`, `script_id`, and `packet_id`, and keeps follow-up candidates as `seed`.
  - Episode append records can carry source-role coverage, critical-view use, compact claims, open questions, and follow-up seeds, but cannot carry raw article body, private data, full narration text, runtime DB paths, proof/screenshot paths, YMM4 geometry, subtitle coordinates, `.ymmp`, or overlay proof.
  - This is not second-episode generation, follow-up seed promotion, autonomous recommendation, source candidate promotion, dashboarding, publishing strategy, NLMYTGen integration, DB migration, or runtime export mutation.
  - Validation: channel-memory append tests -> 15 passed; full `.venv\Scripts\python.exe -m pytest -q` -> 106 passed; `git diff --check` -> passed; active export inspect remained PASS / `No issues found.`
- M7-D source-role backfill on 2026-06-08:
  - Backfilled the active `docs\channel_memory\copilot_watch.yml` source-role coverage from existing authority only.
  - `article_f4124bbb866ef6b0` now reads as Microsoft Blog `microsoft_official` / `vendor_official`.
  - `article_bfba4cd5131daa71` now reads as NIST `standards_body` / `standards_body`, including the critical-view row.
  - Follow-up candidates remain `seed`; no source candidate was promoted, no story was selected, and no runtime DB/export/proof artifact was committed.
  - Validation: channel-memory tests -> 16 passed; full `.venv\Scripts\python.exe -m pytest -q` -> 107 passed; `git diff --check` -> passed; active series report has no `unclassified / no_pool`; active export inspect remained PASS / `No issues found.`
- Local validation after the P0.5-D approved materialization apply:
  - `.venv\Scripts\python.exe -m pytest -q` -> 72 passed.
  - `git diff --check` -> passed.
  - `.venv\Scripts\python.exe -m newsroom.cli.main export inspect --episode-dir data\exports\episode_756343df9853` -> PASS with `script_todo_skeleton` absent and `critical_view` absent.
- Local validation after the P1 remaining visual/asset/screenshot gate:
  - Targeted visual/asset/quote/export tests -> 33 passed.
  - `.venv\Scripts\python.exe -m pytest -q` -> 77 passed.
  - `git diff --check` -> passed.
- Local validation after the P1 broad script review gate:
  - Targeted script/export tests -> 23 passed.
  - `.venv\Scripts\python.exe -m pytest -q` -> 78 passed.
  - `git diff --check` -> passed.
- Local validation after the P1 operator script review decision apply path:
  - Targeted materialization/export/inspector tests -> 38 passed.
  - `.venv\Scripts\python.exe -m pytest -q` -> 81 passed.
  - `git diff --check` -> passed; Git reported a CRLF-to-LF normalization warning for the approved materialization YAML.
  - `.venv\Scripts\python.exe -m newsroom.cli.main export inspect --episode-dir data\exports\episode_756343df9853` -> PASS with no issues found.
- Local validation after the P1 Packet persistence slice:
  - Targeted packet/storage tests -> 13 passed.
  - `.venv\Scripts\python.exe -m pytest -q` -> 85 passed.
  - `git diff --check` -> passed.
  - Active runtime packet persisted with `newsroom packet build --story story_20260603_503c39418f15862d`; `packet show --story story_20260603_503c39418f15862d` read back `packet_20260603_2de578dcd4b0` with 1 primary source and 1 C1/NIST critical view.
  - Rebuilt visual/asset/quote/export for `script_d2a46430e084`; `export inspect --episode-dir data\exports\episode_756343df9853` -> PASS with no issues found.
- Local validation after the P0.5-C approved authority slice:
  - `.venv\Scripts\python.exe -m pytest tests\test_script_materialization.py -q` -> 17 passed.
  - `.venv\Scripts\python.exe -m pytest -q` -> 72 passed.
  - `git diff --check` -> passed.
  - Active `newsroom script approve-materialization` rejected the unfilled/unapproved runtime draft as expected.
  - Active `export inspect` remained PASS with `script_todo_skeleton` still present and `critical_view` absent.
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
- Implementation frontier: M1 through M6.4 are implemented; P0-A CSV import acceptance is proven for the active YMM4 export after adding the `ナレーター` character in the target YMM4 environment; P0-B critical-view source entry has a DB-backed CLI path and has been exercised on the active story with C1/NIST; P0.5 approved materialization authority is implemented and applied to the active script; P1 quote/visual/asset/script review gates are applied for the active export; P1 Packet persistence is implemented for DB-backed NotebookPacket rows and downstream reuse; P2 source pools, the first M7 channel-memory seed, M7-B readback, M7-C append workflow, and M7-D source-role backfill are implemented.

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
- state: complete for the active script. Operator approved all 6 suggestion rows, `docs\approved_materializations\script_d2a46430e084.materialization.yml` is the tracked sanitized narration authority, the record was applied to DB ScriptIR and the refreshed script bundle, and the active export was rebuilt. `export inspect --episode-dir data\exports\episode_756343df9853` passes with `script_todo_skeleton` absent and `critical_view` absent.
- authority: durable approved narration authority is `docs\approved_materializations\script_d2a46430e084.materialization.yml`. Runtime draft, DB rows, export bundle, and proof files remain checkout-local runtime evidence and are not committed.
- owner: assistant for tooling/rebuilds and operator for editorial approval of final narration.
- next move: continue with the remaining publication/operator gates. Do not treat this as YMM4 subtitle placement, overlay safety, final geometry, `.ymmp`, or publishing proof.

### P1: QuoteManifest tightening

- purpose: reduce noisy `human_required` quote rows.
- effect: review focuses on direct quote / screenshot / data-use intent instead of every source-backed segment.
- requirements: distinguish citation-only `source_refs` from direct quote or screenshot intent.
- state: implemented for the active path. Ordinary source-reference text rows now carry `review_level: source_reference` / `approval_state: citation_only`; direct quote, screenshot-candidate, and data-use intent remain `human_required`. Earlier generated runtime artifacts may still show the old `review_level: citation_only` label until regenerated. The subsequent visual/asset/screenshot gate removed the active screenshot intent. The 5 C1/NIST rows remain present as `source_role: critical_view`.
- owner: assistant.
- next move: superseded by the remaining visual/asset/screenshot gate below for the active export. Do not use QuoteManifest tightening to clear `speculation_vs_fact` or broad `needs_human_review`.

### P1: Remaining visual/asset/screenshot review gate

- purpose: classify concrete visual/source-card review items without suppressing unrelated publication warnings.
- effect: citation-only source evidence no longer creates an external screenshot gate by default.
- requirements: preserve source refs, C1/NIST coverage, `source_card` as an explicit human-required screenshot intent, and the downstream subtitle/YMM4 geometry boundary.
- state: implemented for the active export. The facts visual unit now uses `claim_evidence_card` with Microsoft source refs preserved; AssetManifest uses local templates; QuoteManifest has 10 citation-only text rows and 0 screenshot rows. This gate was later superseded by the broad script review decision apply path, and active `export inspect` now passes with no issues found.
- owner: assistant for generator behavior and rebuilds; operator for any future explicit external screenshot/source-card approval.
- next move: superseded by the broad script review gate below for the active export. Do not treat the absence of visual/asset/quote `human_required` as publishing approval.

### P1: Broad script review gate

- purpose: classify `speculation_vs_fact` and broad segment `needs_human_review` without clearing them by heuristic.
- effect: operator can review the remaining publication gates from a tracked handoff artifact without changing approved narration authority.
- requirements: preserve approved text, speaker `ナレーター`, source refs, C1/NIST critical refs, claim types, and visual/asset/quote cleared state.
- state: complete for the active script after explicit operator/editorial decision. `docs\approved_materializations\script_d2a46430e084.materialization.yml` now contains the final approved text for this slice and clears `human_review_required` for all 6 segments; `docs\script_review_gates\script_d2a46430e084.review.yml` records the operator-cleared `needs_human_review` and `speculation_vs_fact` decisions. Active `export inspect` passes with no issues found.
- owner: operator/editor for approval authority; assistant for applying the tracked authority and rebuilds.
- next move: continue to Packet persistence or a concrete downstream YMM4 visual/subtitle proof only if explicitly requested. Do not treat this script-review clearance as publishing/legal/YMM4 visual/subtitle/overlay/final-geometry approval.

### P1: Packet persistence

- purpose: store NotebookPacket records as first-class DB rows.
- effect: operator packet edits and critical-view additions survive downstream rebuilds.
- requirements: DB schema, load/upsert helpers, migration-safe existing DB behavior, and CLI readback.
- state: implemented. `notebook_packets` persists sanitized packet records in the runtime DB. `packet build` upserts the packet, `packet show` reads it back, and downstream helpers prefer persisted packet state while merging newly required critical-view refs.
- owner: assistant.
- next move: validate or regenerate the active runtime packet/export if needed, or continue to the next scoped backlog item. Do not treat packet persistence as NotebookLM API automation or publishing approval.

### P2: Source expansion

- purpose: add deliberate source pools while preserving RSS-first intake and manual approval boundaries.
- effect: story selection and packet quality can distinguish vendor, regulator, standards, independent analysis, technical reference, and critical-view candidate sources without collecting everything.
- requirements: source pool metadata only, no tracked raw article bodies, no private data, no OAuth/token flow, no NotebookLM automation, and no automatic adoption of critical-view candidates.
- state: implemented. `configs\source_pools.yml` defines the allowed roles and pools; `configs\sources.yml` feed rows can reference a pool; RSS articles and packet source refs preserve `source_role` / `source_pool_id`; `critical_view_candidate` is not automatically added to `packet.critical_views`.
- owner: assistant for registry/tooling behavior; operator/editor for deciding which candidate sources become active story or critical-view inputs.
- next move: use the registry to add or tune feed metadata deliberately, then continue to M7 series/channel memory or another explicitly scoped backlog item. Do not expand this into broad crawling, Inoreader OAuth, NotebookLM automation, or automatic source adoption.

### M7: Channel memory seed

- purpose: connect the active approved episode to series continuity without turning the repo into an autonomous recommendation engine.
- effect: future planning can see prior episode ids, compact claims, source-role coverage, NIST critical-view use, open questions, and follow-up seeds.
- requirements: tracked sanitized YAML only, no raw article body, no private data, no full narration copy, no runtime DB/export/proof authority, and no automatic source or topic adoption.
- state: implemented as the first narrow slice. `docs\channel_memory\copilot_watch.yml` records the active episode and next-episode seeds; `newsroom.editorial.channel_memory` validates that records stay schema-safe and do not contain forbidden fields.
- owner: assistant for schema/tooling; operator/editor for deciding which follow-up seed becomes an actual story.
- next move: add a small report or append workflow only after another episode exists or the operator asks to promote a follow-up seed. Do not expand this into dashboarding, scraping, or publishing strategy.

### M7-B: Series report readback

- purpose: make tracked channel memory readable from the CLI without editing DB/export/runtime state.
- effect: an operator can inspect series continuity, source-role coverage, critical-view use, compact claims, open questions, and follow-up seeds before deciding the next story.
- requirements: read `docs\channel_memory\<series_id>.yml`; render only; do not auto-select stories, promote source candidates, or mutate runtime artifacts.
- state: implemented. `newsroom series report --series copilot_watch` reads the tracked memory record and prints the report with an explicit note that follow-up seeds are not approved stories.
- owner: assistant for report tooling; operator/editor for any future story selection.
- next move: add append/report refinements only when a second episode exists or a manual promotion decision is returned.

### M7-D: Source-role backfill

- purpose: remove legacy `unclassified / no_pool` readback from the active `copilot_watch` memory record without inventing source decisions.
- effect: series continuity now shows Microsoft Blog as `vendor_official / microsoft_official` and NIST as `standards_body / standards_body`.
- requirements: use only explicit source authority from tracked config and the already adopted C1/NIST critical-view context; preserve follow-up seeds as seeds.
- state: implemented for `episode_756343df9853`. Active `series report --series copilot_watch` has no `unclassified / no_pool`, and active export inspect remains PASS / `No issues found.`
- owner: assistant for metadata hygiene; operator/editor for any future source/story adoption.
- next move: wait for an operator-approved second episode record, an explicit follow-up seed selection, or a concrete downstream failure. Do not expand this into crawling, autonomous recommendation, NotebookLM automation, YMM4 geometry, or publishing work.

## Boundaries

- NotebookLM remains a manual packet bridge; no NotebookLM API automation.
- YMM4 GUI operation is operator-owned; this repo prepares files and proof templates.
- Newsroom YMM4 proof is limited to CSV import acceptance and handoff-file readability; subtitle placement authority, YMM4 item geometry, template positioning, subtitle band decisions, `.ymmp` patch details, and overlay proof belong downstream.
- Full `.ymmp` generation is out of scope.
- YouTube upload and publishing are out of scope.
- Inoreader OAuth/token flow is deferred.
- External image download and automatic external asset approval remain out of scope.
- NLMYTGen integration is schema-only: CSV / JSON / Markdown handoff, not subprocess, path dependency, pip dependency, or shared code.
- Source expansion is metadata-first and RSS-first. Source pools classify feeds and packet refs; they do not fetch broad web content, scrape raw articles into tracked artifacts, or approve candidates automatically.
- Channel memory is tracked editorial continuity only. It stores compact episode memory and planning seeds; it does not recommend, fetch, publish, or approve topics automatically.

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
