# Project Rule Alignment - 2026-06-14

Run date: 2026-06-15 JST.

This packet aligns the current `newsroom-yt-pipeline` / `NLMYTGen`
handoff-supervision state with the updated operating rules. It is a docs-only
audit. It does not start Newsroom ingest, NLMYTGen adapter work, YMM4 geometry,
rendering, publishing, context visual generation, or runtime artifact transfer.

## Current Recheck

Latest live recheck on 2026-06-15 JST:

- Newsroom was synced on `main` at baseline commit `0b859bd docs: align project
  handoff rules`, with `HEAD...@{u}=0 0` before this docs-only packet refresh.
  The working tree was clean before editing this document.
- NLMYTGen was synced on `master` at `4746d81 docs: design live repo status
  producer`, with `HEAD...@{u}=0 0`. Tracked and staged state stayed clean.
  Untracked `.claude/worktrees/jolly-albattani-d6dd78/` and
  `samples/2026-05-16.ymmp` were observed and left untouched.
- `newsroom series report --series copilot_watch` still reports
  `newsroom_handoff_clean`, Microsoft Blog as
  `vendor_official / microsoft_official / official`, NIST as
  `standards_body / standards_body / official`, and follow-up candidates as
  `seed`.
- `newsroom export inspect --episode-dir data\exports\episode_756343df9853`
  still returns `PASS` / `No issues found`.
- `data/exports/episode_756343df9853` is still ignored by `.gitignore`, and no
  files from that export are tracked.
- Classification remains `request_authority`: the export is a valid upstream
  candidate, but NLMYTGen downstream intake still needs human authority.

## Classification

- Current state: `request_authority`.
- Newsroom export state: valid upstream handoff candidate.
- NLMYTGen state: downstream intake is not authorized yet.
- Stale prompt handling: supersede before use.
- Cross-repo transfer state: hold until a human chooses copy-in, read-only
  review, or continued hold.

## Inspected Repos

### Newsroom

Observed local repo:

- `C:\Users\thank\Storage\Media Contents Projects\newsroom-yt-pipeline`
- Branch: `main`
- Live recheck baseline HEAD before this packet refresh: `0b859bd`
- Latest commit at recheck baseline: `0b859bd docs: align project handoff rules`
- Upstream parity after sync: `HEAD...@{u}=0 0`
- Tracked/staged/untracked state after sync: clean

The requested legacy path
`C:\Users\PLANNER007\newsroom-yt-pipeline` was not present on this machine. That
path is a stale local reference, not canonical authority.

### NLMYTGen

Observed local repo:

- `C:\Users\thank\Storage\Media Contents Projects\NLMYTGen`
- Branch: `master`
- HEAD: `4746d81`
- Latest commit: `4746d81 docs: design live repo status producer`
- Upstream parity after sync: `HEAD...@{u}=0 0`
- Tracked and staged state: clean
- Known untracked residue left untouched:
  - `.claude/worktrees/jolly-albattani-d6dd78/`
  - `samples/2026-05-16.ymmp`

## Authority Docs Read

Newsroom:

- `README.md`
- `docs/HANDOFF.md`
- `docs/RUNTIME_STATE.md`
- `docs/META_REVIEW_LEDGER.md`
- `docs/verification/NEWSROOM-HANDOFF-INVENTORY-2026-06-10.md`
- `docs/channel_memory/README.md`
- `docs/channel_memory/copilot_watch.yml`
- `docs/PROJECT_SPEC.md`

NLMYTGen:

- `AGENTS.md`
- `docs/REPO_LOCAL_RULES.md`
- `docs/runtime-state.md`
- `docs/project-context.md`
- `docs/AGENT_ORCHESTRATION.md`
- `docs/AGENT_OPERATOR_SURFACE.md`
- `docs/USER_COPYPASTE_BLOCKS.md`
- `docs/verification/NEWSROOM-HANDOFF-SUPERVISION-GATE-2026-06-09.md`
- `.agent/state.json`
- `.agent/repo_adapter.json`
- `.agent/prompt_catalog/advance.md`
- `.agent/prompt_catalog/audit.md`
- `.agent/prompt_catalog/fix.md`
- `.agent/prompt_catalog/summarize.md`

## Active Artifacts

### Newsroom

Active export candidate:

- `data/exports/episode_756343df9853`
- The folder is ignored runtime output and is not tracked authority.
- Current checkout contains 9 handoff files:
  - `asset_manifest.yml`
  - `export_manifest.json`
  - `quote_manifest.yml`
  - `script.csv`
  - `script_ir.json`
  - `source_list.md`
  - `visual_ir.json`
  - `visual_plan.md`
  - `ymm4_notes.md`

Live readback:

- `newsroom series report --series copilot_watch` reports status
  `newsroom_handoff_clean`.
- Follow-up candidates remain `seed`; they are not approved stories.
- Source-role coverage reports Microsoft Blog as
  `vendor_official / microsoft_official / official` and NIST as
  `standards_body / standards_body / official`.
- `newsroom export inspect --episode-dir data\exports\episode_756343df9853`
  returns `PASS` and `No issues found`.

Tracked handoff authority remains:

- `docs/verification/NEWSROOM-HANDOFF-INVENTORY-2026-06-10.md`
- `docs/HANDOFF.md`
- `docs/RUNTIME_STATE.md`
- `docs/channel_memory/copilot_watch.yml`

### NLMYTGen

Active NLMYTGen authority still comes from:

- `AGENTS.md`
- `docs/REPO_LOCAL_RULES.md`
- `docs/runtime-state.md`

The valid cross-repo gate record is:

- `docs/verification/NEWSROOM-HANDOFF-SUPERVISION-GATE-2026-06-09.md`

That gate remains valid for its decision state: the Newsroom handoff is
candidate downstream input, not NLMYTGen authority. It does not authorize
copy-in, read-only path pinning, adapter implementation, Review Console changes,
`.ymmp` generation, render, production, rights approval, or publishing.

The `.agent/` worker prompt catalog remains inert preview/common-foundation
support. It is not permission to run a real Codex runner, start a worker loop,
write reports, or treat worker reports as production approval.

## Valid Handoff Records

- Newsroom `docs/verification/NEWSROOM-HANDOFF-INVENTORY-2026-06-10.md` remains
  valid as a prior inventory of the active export package and its partial
  readiness.
- Newsroom `docs/HANDOFF.md` and `docs/RUNTIME_STATE.md` remain valid because
  they state the handoff is partial and requires explicit human decision before
  NLMYTGen transfer.
- NLMYTGen
  `docs/verification/NEWSROOM-HANDOFF-SUPERVISION-GATE-2026-06-09.md` remains
  valid as the current authority gate: `request_authority / no-op_wait`.
- NLMYTGen `docs/USER_COPYPASTE_BLOCKS.md` Section 21 remains useful as
  historical gate context, but it must be superseded before reuse because some
  repo-state details are stale.

## Stale Prompts Or Prompt Patterns

| Location | State | Effect | Next move |
|---|---|---|---|
| Newsroom `docs/verification/NEWSROOM-HANDOFF-INVENTORY-2026-06-10.md` | Stale local absolute path and stale HEAD snapshot. | It records `C:\Users\PLANNER007\newsroom-yt-pipeline` and `a89b8e4`, while the current observed repo is under `C:\Users\thank\Storage\Media Contents Projects\newsroom-yt-pipeline` and was rechecked at baseline `0b859bd` before this packet refresh. | Keep as prior inventory; use this packet plus fresh git commands for the current machine/path/HEAD readback. |
| NLMYTGen `docs/verification/NEWSROOM-HANDOFF-SUPERVISION-GATE-2026-06-09.md` | Valid decision, stale repo-state facts. | It records Newsroom at `1296b8e`; current synced Newsroom was rechecked at baseline `0b859bd` before this packet refresh. | Keep the decision; refresh state facts before any downstream intake. |
| NLMYTGen `docs/USER_COPYPASTE_BLOCKS.md` Section 21 | Superseded for the next worker prompt. | It carries the old Newsroom HEAD and a prior `BEGIN_COPY_BLOCK_FOR_CHATGPT` report wrapper. | Do not execute blindly. Use the replacement prompt in this packet. |
| NLMYTGen `docs/USER_COPYPASTE_BLOCKS.md` older sections | Stale local path examples. | Several older restart prompts mention `C:\Users\PLANNER007\NLMYTGen`; that path is not the observed repo in this run. | Treat as historical unless a future environment verifies that path live. |
| NLMYTGen `docs/project-context.md` and `docs/runtime-state.md` historical entries | Mixed historical snapshots. | Some entries correctly preserve prior environment facts but are not current readback for this machine. | Use only the latest current-state sections plus fresh git commands for restart. |
| NLMYTGen `.agent/prompt_catalog/*.md` | Valid only inside the inert worker-report contract. | The prompts require JSON worker reports and mention single-code-block completion behavior; they are not the current human supervision report contract. | Do not use them as the next Newsroom/NLMYTGen handoff worker prompt. |

## Old Reporting Style Contamination

Old reporting style remains in reusable prompt material, mostly as historical
copy/paste contracts:

- `docs/USER_COPYPASTE_BLOCKS.md` Section 21 asks for
  `BEGIN_COPY_BLOCK_FOR_CHATGPT` / `END_COPY_BLOCK_FOR_CHATGPT`.
- `.agent/prompt_catalog/*.md` requires worker JSON and treats
  single-code-block completion violations as gate risks.
- `docs/AGENT_ORCHESTRATION.md` documents that worker-report contract.

These are not wrong for their original owner context, but they should not be
used as the next cross-repo supervision prompt. The next prompt should use the
updated section-only Markdown report contract and avoid connector/UI directive
lines.

## Repo-Boundary Risks

- A Newsroom ignored export path is live evidence, not portable NLMYTGen
  authority.
- Pinning a local read-only path in NLMYTGen would make NLMYTGen depend on one
  checkout unless a human explicitly authorizes that as a candidate reference.
- Copying export files into NLMYTGen would create canonicality and provenance
  questions that have not been answered.
- NLMYTGen must not gain Newsroom subprocess, path, pip, or shared-code
  dependency.
- Newsroom must not inherit downstream YMM4 geometry, subtitle placement,
  overlay proof, `.ymmp`, render, production, or publishing authority.
- Rights, legal, production, and publishing decisions remain human-owned and
  ungranted.

## Artifact Visibility Gaps

- `data/exports/episode_756343df9853` is present in this Newsroom checkout, but
  it is ignored runtime output. A different checkout must recheck or regenerate
  before relying on it.
- The prior Newsroom inventory says there is no path mismatch; that was true for
  its observed environment, but the literal `PLANNER007` Newsroom path is absent
  in this run.
- NLMYTGen Section 21 says Newsroom was at `1296b8e`; the current synced
  Newsroom head is `223c9aa`.
- NLMYTGen has untracked local residue, including an untracked `.ymmp`. It was
  not touched, staged, or promoted.
- No current artifact grants NLMYTGen copy-in, read-only pinning, adapter
  implementation, Review Console change, render, production, rights, or
  publishing authority.

## Decision Packet

### Option 1 - Hold

- Purpose: preserve the clean supervision baseline without starting downstream
  intake.
- Effect: keeps Newsroom handoff as a valid upstream candidate and NLMYTGen on
  its current authorized lanes.
- Requirements: no further action beyond this packet.
- State: valid now.
- Owner: human owner for any future restart.
- Next move: supply an explicit decision later if NLMYTGen should inspect or
  copy the package.
- Risk: no adapter progress occurs.

### Option 2 - Read-Only NLMYTGen Review

- Purpose: let NLMYTGen inspect the live Newsroom export without copying it.
- Effect: can produce a docs-only intake plan or manifest mapping while keeping
  Newsroom artifacts in place.
- Requirements: explicit human authorization to use the observed Newsroom path
  as a candidate read-only reference, plus confirmation that G-28 can pause or
  remain secondary during the review.
- State: not authorized yet.
- Owner: human for authority; assistant for readback and docs-only mapping.
- Next move: run live repo/export checks again, then write a narrow NLMYTGen
  docs-only intake plan.
- Risk: local path lifetime remains fragile.

### Option 3 - Copy-In Snapshot

- Purpose: make selected Newsroom files stable inside NLMYTGen.
- Effect: removes dependency on the ignored Newsroom export folder after copy.
- Requirements: explicit human decision naming which files become canonical,
  provenance wording, and whether the copied files are candidate review inputs
  only.
- State: not authorized yet.
- Owner: human for canonicality; assistant for explicit-file copy and manifest.
- Next move: create a copy manifest before copying any file.
- Risk: copied candidate files could be mistaken for production, rights, or
  render approval if not labeled carefully.

### Option 4 - Supersede Current Prompt Only

- Purpose: retire the stale Section 21 restart prompt without starting intake.
- Effect: creates a fresh copyable prompt that future agents can use safely.
- Requirements: no runtime artifact work; docs-only prompt replacement or a
  new verification record.
- State: this packet supplies the replacement prompt.
- Owner: assistant for docs; human for later intake authority.
- Next move: use the prompt below for the next worker.
- Risk: NLMYTGen still needs a future explicit authority decision before
  downstream work begins.

Recommended default: Option 1 now, with Option 2 as the first active path if
the human wants NLMYTGen to proceed. Holding is the cleanest current baseline
because the live export is valid but the cross-repo authority decisions are
still absent.

What remains undecided:

- Whether NLMYTGen should copy files, inspect by read-only path, or keep holding.
- Whether G-28 should pause, remain active, or be superseded by Newsroom intake.
- Which first NLMYTGen output is wanted: docs-only intake plan, manifest mapping,
  or adapter implementation.
- Which files, if any, become canonical NLMYTGen artifacts.

What can proceed without that decision:

- Docs-only state refresh.
- Live git/export parity checks.
- Stale prompt retirement.
- A replacement next-worker prompt that stops at authority.

## Recommended Next Worker Prompt

Use this prompt instead of NLMYTGen `docs/USER_COPYPASTE_BLOCKS.md` Section 21:

```text
Task: Recheck the Newsroom/NLMYTGen handoff supervision gate under the updated project rules. Do not start feature work.

Scope:
- Newsroom repo: C:\Users\thank\Storage\Media Contents Projects\newsroom-yt-pipeline
- NLMYTGen repo: C:\Users\thank\Storage\Media Contents Projects\NLMYTGen
- Treat any other absolute path in older docs as historical until verified live.

Start by running these commands in both repos if present:
- git status --porcelain=v1 --untracked-files=all
- git status --porcelain=v1 -uno
- git fetch --prune origin
- git pull --ff-only
- git branch --show-current
- git rev-parse --short HEAD
- git rev-list --left-right --count "HEAD...@{u}"
- git log -1 --oneline
- git diff --name-only
- git diff --cached --name-only

Read authority docs before changing anything.

Newsroom read order:
- README.md
- docs/HANDOFF.md
- docs/RUNTIME_STATE.md
- docs/META_REVIEW_LEDGER.md
- docs/verification/PROJECT-RULE-ALIGNMENT-2026-06-14.md
- docs/verification/NEWSROOM-HANDOFF-INVENTORY-2026-06-10.md
- docs/channel_memory/README.md
- docs/channel_memory/copilot_watch.yml

NLMYTGen read order:
- AGENTS.md
- docs/REPO_LOCAL_RULES.md
- docs/runtime-state.md
- docs/project-context.md latest supervision gate section
- docs/verification/NEWSROOM-HANDOFF-SUPERVISION-GATE-2026-06-09.md
- docs/USER_COPYPASTE_BLOCKS.md Section 21 only as historical context

Current expected state:
- Newsroom active export candidate is data/exports/episode_756343df9853.
- The export is ignored runtime output and must not be committed.
- Current alignment packet last rechecked Newsroom main at baseline 0b859bd and NLMYTGen master at 4746d81 with both repos at upstream parity; rerun git commands for the exact live HEAD before acting.
- NLMYTGen known untracked residue may include .claude/worktrees/ and samples/2026-05-16.ymmp; do not stage or delete it.
- The handoff decision remains request_authority unless the user explicitly supplies copy-in/read-only/hold and G-28 pause/supersede authority.

Allowed:
- Read-only inspection.
- Docs-only correction of stale handoff/prompt facts.
- A decision packet with 2 to 4 options.
- A replacement next prompt.

Not allowed:
- Runtime DB/export/proof/screenshot changes.
- Copying Newsroom export files into NLMYTGen.
- Pinning a read-only path in NLMYTGen as authority.
- Adapter implementation.
- Review Console changes.
- Context visual generation.
- YMM4 geometry, subtitle placement, overlay proof, .ymmp generation, render, production, rights, legal, or publishing approval.
- NotebookLM API automation, Inoreader OAuth, broad crawling, source auto-adoption, or follow-up seed auto-promotion.
- git add -A.
- Connector/UI directive style lines in the human report.

If no explicit human authority is supplied, stop at request_authority and report:
1. Summary
2. Changed files
3. Artifacts
4. Commands run and results
5. Validation
6. Decision packet, if user judgement is needed
7. Blockers, only if true stop condition
8. Next complete prompt for another Agent
```

## Validation Plan

Required after docs-only changes:

- `git diff --check`
- `git diff --cached --check`

Pytest is not required for this packet because no scripts, tests, GUI, source,
or runtime artifacts are changed.
