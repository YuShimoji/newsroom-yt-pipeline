# Development Practices

This document is the repository-level authority for how to continue development safely. It does not replace the product specification, runtime state, or operator proof records. When there is a conflict, prefer the more specific authority listed below.

## Source Of Truth Hierarchy

| Document | Use it for | Restart priority |
| --- | --- | --- |
| `docs/RUNTIME_STATE.md` | Current state, validation results, next candidates, unfinished items, and checkout-sensitive runtime notes. | Highest for restart decisions. |
| `docs/PROJECT_SPEC.md` | Product scope, responsibility boundary, milestones, non-goals, and decision records. | Higher than older briefs when scope is unclear. |
| `docs/YMM4_IMPORT_PROOF.md` | Operator-run YMM4 CSV import proof procedure and proof boundaries. | Required before handling import-proof records. |
| `README.md` | Overview, install, entry points, and historical M1 context. | Useful entry point, not the active frontier by itself. |
| `docs/AGENT_BRIEF.md` | Initial implementation brief and legacy agent handoff context. | Lower priority than runtime state for restart decisions. |

`docs/HANDOFF.md`, `docs/META_REVIEW_LEDGER.md`, `docs/NLMYTGEN_BOUNDARY.md`, and `docs/verification/` records are supporting authority when a task touches restart order, supervision decisions, downstream handoff, or audit evidence.

## NEXT_ACTION Protocol

Use one active lane at a time. Do not mix implementation lanes unless an explicit task says to do so.

| NEXT_ACTION | Meaning | Allowed movement |
| --- | --- | --- |
| `autonomous_foundation_run` | Autonomous foundation work before human preview is unavoidable. | Docs governance, fixtures, schemas, tests, CLI inspect/readback, and reviewable artifact preparation. |
| `restart_check` | State check, validation, and docs alignment only. | Read authority docs, run validation, update runtime notes if needed. |
| `record_ymm4_import_proof` | Ingest operator-provided proof YAML, screenshot path, YMM4 version, and result. | Update repo records only from operator-provided evidence. |
| `critical_view_source_path` | Durable path for critical, counter, and supporting source handling. | Synthetic fixtures, source classification, packet/readback behavior, and tests. |
| `quote_manifest_tightening` | Separate direct quote, screenshot candidate, data-use, and ordinary source reference semantics. | Manifest schema/readback/tests without clearing review gates. |
| `packet_persistence` | Make NotebookPacket less artifact-only and more durable as record/readback. | DB record/readback, CLI inspect, and downstream reuse. |
| `source_expansion` | RSS-first source expansion without broad crawler, OAuth, or feed-rescue blockers. | Source config, OPML import, sanitized source smoke, and read-only fetch paths. |
| `series_memory` | P2/M7 lane for approved continuity records. | Do not implement or append without explicit selection and approved input. |

## Default No-op Rule

No-op is valid when progress would require missing human approval, a missing operator artifact, or an explicit selected seed. No-op must not block safe foundation work such as synthetic fixtures, schema/readback checks, docs governance, unit tests, CLI inspect paths, or review packet preparation. A follow-up seed is not an approved story and must not be promoted automatically.

## Preview Gate Policy

Human preview is required for final script acceptance, quote approval, external image or screenshot approval, audio license choices, defamation or privacy-sensitive claims, YMM4 GUI import proof acceptance, public release, legal or rights judgement, and publishing decisions.

Human preview is not required for synthetic fixtures, schema/readback work, CLI inspect commands, docs governance, unit tests, deterministic manifest structure, or local diagnostic output that does not assert editorial approval.

When preview becomes necessary, prepare a decision packet before stopping. Include the repo-relative files to open, commands to run, observation points, expected pass/fail signals, fallback path, one recommended default, and rejected alternatives.

## Freeform Review And Autonomy

User-facing review requests must accept freeform comments. Do not require fixed labels or phrases such as `accept`, `reject`, or `small_adjustment`. Agents may internally normalize a freeform response into target, intent, constraints, and confidence, but the user should not be asked to rewrite feedback into labels.

When an artifact needs review, include a Review Card near the artifact access details. The card should name the target, list no more than three things to look at, state that freeform review is accepted, give natural examples of useful feedback, and explain how the agent will interpret the response and continue. If review would be useful later but is not a stop condition, record it as Review Debt and keep working. If no review is needed, state that Review Card / Review Debt is none.

Use long-run autonomy for in-scope, reversible work. When no true stop condition is present, execute the next one to three scoped actions instead of only listing them. If validation fails, form a narrow hypothesis and try at least one scoped fix before stopping. Stop only for real blockers such as destructive changes, unresolved branch divergence, missing approval for an irreversible boundary, validation failing twice after a scoped fix, or low-confidence review interpretation that would materially change artifact direction.

## Boundary Rules

`newsroom-yt-pipeline` owns upstream editorial OS concerns: RSS/source selection, article ledger, clustering, scoring, rights index, VisualIR, AssetManifest, QuoteManifest, review packets, and future approved series memory.

`NLMYTGen` is a downstream adapter for NotebookLM/YMM4-oriented conversion. Prefer schema and artifact boundaries over shared GUI code, subprocess coupling, local path dependencies, or moving newsroom decisions downstream.

## Human Approval Gates

Keep human approval for quotes, external images and screenshots, audio license choices, defamation or privacy-sensitive claims, final scripts, and publishing decisions. Do not erase `human_required`, rights, speculation, or approval warnings merely to make tests pass.

QuoteManifest and AssetManifest are review indexes. They are not automatic legal clearance, publication approval, or final asset-use approval.

In QuoteManifest rows, `review_level: source_reference` means an ordinary source reference or attribution row. It is distinct from `review_level: direct_quote`, `review_level: screenshot_candidate`, and `review_level: data_use`, which remain human-review intents when present. `approval_state: citation_only` may be used for source-reference rows, but it is not a direct-quote, screenshot, or data-use approval.

## Evidence Discipline

Completion claims must include the commands run, validation results, changed files, artifact paths when artifacts exist, and repo state. Distinguish implemented, inspected, generated, diagnostic-only, and operator-pending states.

Do not claim YMM4 GUI import proof from CLI export inspection alone. `newsroom export inspect` can validate bundle consistency; it cannot prove YMM4 accepted the CSV, subtitle placement, overlay safety, final geometry, render quality, or publishing readiness.

## Operation Cockpit Closeout

Use an Operation Cockpit closeout for restart, handoff, review-access, artifact, or supervision work. The closeout should make the current state, expected-versus-actual result, changed files, review artifacts, Review Card / Review Debt, Freeform Review Intake Result, command/action ledger, user-side work, agent-side next actions, goal contribution, decision packet, and continuation state visible without requiring the reader to reopen every file.

For reviewable artifacts, report identity and access separately. Identity should include `artifact_id`, repo-relative path, manifest location when one exists, and the source of truth. Access should be one of a preview URL, a repo-local launcher, an open command with shell and cwd, or a verified temporary full path only as supplemental evidence.

Action ledger entries should identify whether the action was executed by the agent, left for the agent to run later, required from the user, user-open-only, user freeform review, reference-only, or explicitly out of scope. Use `USER_REVIEW_FREEFORM` when the user is invited to review an artifact in natural language. Keep next actions short and concrete; do not include a full next-agent prompt unless a fresh handoff gate is actually triggered.

## Repository Hygiene

Do not commit raw real news bodies, large real URL or title lists, raw OPML, secrets, tokens, private local traces, runtime DBs, generated export bundles, proof screenshots, or operator-private evidence.

Use anonymized fixtures and synthetic examples for implementation and tests. Do not make dead feed rescue, OAuth integration, GUI automation, NotebookLM live execution, or external publishing a blocker for local schema, docs, test, and readback work.

PR creation is not the default workflow. Prefer local diff, tests, and commit-boundary evidence unless the user explicitly asks for a push or pull request.

## Local Documentation View

The MkDocs browser view is a review surface only. It may make existing Markdown easier to inspect or browser-translate, but it must not become a translated or summarized replacement for source documents.

The `.docs-view/` tree is tracked as MkDocs source, not as generated output. Keep files there as thin snippet wrappers around the canonical Markdown paths, and keep generated HTML under the ignored `.mkdocs-site/` directory. When source Markdown is added, update the wrapper and `mkdocs.yml` nav deliberately; use `tools\generate-doc-nav.ps1` only as a candidate generator.
