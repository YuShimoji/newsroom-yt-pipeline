# Development Practices

Last updated: 2026-06-15

This document fixes the restart rules for `newsroom-yt-pipeline`. It is not a
roadmap, status log, or implementation history. When project direction is
ambiguous, use these rules to decide whether to proceed, stop, or ask for a
specific operator artifact.

## Source of Truth Hierarchy

1. `docs/RUNTIME_STATE.md`
   - Current checkout state, validation results, next candidates, and incomplete
     or unproven work.
2. `docs/PROJECT_SPEC.md`
   - Product specification, responsibility boundaries, and explicit non-goals.
3. `docs/YMM4_IMPORT_PROOF.md`
   - Operator-run YMM4 import proof procedure. This is the authority for what a
     YMM4 proof can and cannot claim.
4. `README.md`
   - Project overview and navigation. The M1 section is retained as initial MVP
     context, not as the current development frontier.
5. `docs/AGENT_BRIEF.md`
   - Initial implementation brief. For restart decisions, prefer
     `docs/RUNTIME_STATE.md`.

If a referenced file is missing, treat the reference as stale and continue from
the nearest available authority.

## NEXT_ACTION Protocol

`NEXT_ACTION` controls what work is allowed in the current run.

| NEXT_ACTION | Allowed work | Stop condition |
| --- | --- | --- |
| `autonomous_foundation_run` | Continue through preview-free foundation work: docs, tests, schemas, fixtures, CLI inspect/readback, and small implementation slices inside existing boundaries. | Stop at the first human preview, operator proof, real-news material approval, broad architecture fork, or external irreversible action. |
| `restart_check` | Verify repo state, run baseline tests, read authority docs, and keep governance docs aligned. | Stop after reporting validation and safe next options. Do not implement features. |
| `record_ymm4_import_proof` | Read an operator-created proof YAML, screenshot path, YMM4 version, and import result, then reflect the result in repo docs or runtime state. | Stop if `OPERATOR_PROOF_PATH` is empty or unreadable. Do not operate the YMM4 GUI. |
| `critical_view_source_path` | Create a durable path for an operator to add or classify critical, opposing, or supporting sources. | Stop before automatic source adoption or broad crawling. |
| `quote_manifest_tightening` | Reduce noisy QuoteManifest rows by separating direct quotes, screenshot intent, data-use intent, and citation-only source refs. | Stop before legal approval or publishing claims. |
| `packet_persistence` | Move NotebookPacket from artifact-only handling toward first-class runtime DB records. | Stop before storing raw article bodies, private data, NotebookLM outputs, or publishing proof. |
| `source_expansion` | Expand the source pool while staying RSS-first and metadata-first. | Stop before broad crawlers, Inoreader OAuth, failed-feed rescue as a blocker, or automatic source adoption. |
| `series_memory` | Maintain M7 channel or series memory from approved episode records. | Stop unless the operator supplies an approved episode record or explicit story-selection decision. |

Default priority order for future candidates:

1. P0: operator-run YMM4 GUI import proof intake, when a concrete proof path is
   supplied.
2. P0: critical-view source path.
3. P1: QuoteManifest tightening.
4. P1: Packet persistence.
5. P2: Source expansion.
6. P2: M7 series / channel memory.

Existing completed work may make an item already satisfied for the active path.
Do not reimplement it just because it appears in this priority list.

## Default No-op Rule

If all of the following inputs are empty, preview-dependent lanes are a
`restart_check/no-op` by default:

- `SELECTED_SEED`
- `APPROVED_STORY_ID`
- `EPISODE_RECORD_FULL_PATH`
- `FAILURE_ARTIFACT_PATH`
- `OPERATOR_PROOF_PATH`

No-op is a safe stop condition, not a failure. A seed is not an approved story.
Do not generate an episode, export bundle, script, NotebookLM packet, or YMM4
handoff only from a seed.

No-op does not block preview-free foundation work. If docs, synthetic fixtures,
schema validation, CLI inspect/readback, or focused tests can be improved without
operator approval or real-news material, keep going inside the requested
`NEXT_ACTION`.

## Preview Gate Policy

Human preview is required when accepting video output, final script text, direct
quotes, external images, screenshots, publication claims, voice-library terms,
or YMM4 GUI import proof.

Before that gate, parser behavior, manifests, anonymized fixtures, schema
readback, CLI inspect output, docs, and test coverage are autonomous work.

When a preview gate is reached, report the operator command, target file path,
expected observations, and fallback path for a failed check. Do not stop with
only a vague request for review.

## Boundary Rules

- `newsroom-yt-pipeline` is the upstream editorial OS.
- `NLMYTGen` is the downstream adapter for NotebookLM / YMM4 conversion.
- Newsroom owns RSS, OPML, source-pack selection, article ledger, clustering,
  scoring, rights planning, VisualIR, AssetManifest, QuoteManifest, and series
  memory.
- NLMYTGen owns YMM4 CSV conversion, direction IR, and YMM4 patch support.
- Repo-to-repo integration must prefer schema boundaries: CSV, JSON, Markdown,
  and documented handoff directories. Do not make shared GUI code the
  integration layer.

## Human Approval Gates

Keep human approval for:

- Quotes.
- External images and screenshots.
- Voice library terms.
- Defamation or privacy-sensitive claims.
- Final script text.
- Publishing decisions.

Do not remove `human_required`, rights, or review warnings only to make tests
pass. QuoteManifest and AssetManifest are review indexes, not automatic legal
decisions.

## Evidence Discipline

Completion claims must include the command, test result, generated or updated
file, artifact path when relevant, and repo state. "Should work" or "designed"
is not enough.

YMM4 import proof is not complete from `newsroom export inspect` alone. It also
requires YMM4-side acceptance and an operator proof record. The proof scope is
CSV import acceptance and handoff-file readability only; it does not prove
subtitle placement, overlay safety, final YMM4 geometry, template positioning,
subtitle band decisions, `.ymmp` patch details, render quality, or publishing
approval.

## Repository Hygiene

- Do not commit raw article URL lists, full article title lists from real news,
  large feed URL dumps, raw OPML, tokens, secrets, personal operator proof
  material, screenshots, runtime DB files, or generated export bundles.
- Keep samples and fixtures anonymized and minimal.
- Do not let failed-feed cleanup or individual dead-feed rescue block source
  expansion.
- Treat dead feed rescue as a separate slice.
- PR creation is not the default local development step. Prefer clear branch
  diff, tests, `git diff --check`, and pre/post-change boundary checks.

## Residual Work Reporting

When reporting residual work, include:

- Purpose: why the work exists.
- Effect: what changes when it is done.
- Requirements: concrete inputs or evidence required.
- State: current status, including whether it is blocked, pending, complete, or
  not proven.
- Owner: operator, assistant, or downstream tool/repo.
- Next move: the smallest safe action that can advance it.

## Completion Report Contract

Completion reports must include:

1. Summary.
2. Local repo state.
3. Changed files.
4. Tests / validation.
5. Boundary decisions.
6. Human-required / blocked items.
7. Safe next options.
8. Next prompt.

End the report with one copyable prompt that the next development thread can
use as-is.
