# Meta-Review Ledger

Last updated: 2026-06-04

This ledger preserves supervision decisions that should survive restarts. Keep it short; do not turn it into a runtime-state duplicate.

## 2026-06-04 Gate

- current_task: resume `newsroom-yt-pipeline` after sync and re-audit P0 blocker/artifact boundaries before normal implementation.
- decision: narrow.
- reason: YMM4 GUI import proof is a real operator authority boundary, but it should not block Codex-owned work on the critical-view source-entry path.
- active_artifact: `data\exports\episode_756343df9853` remains the active YMM4 proof target. It passed machine inspection but is not YMM4 GUI-proven.
- true_blockers: YMM4 GUI import, screen check, and proof YAML completion require operator authority.
- stale_or_false_blockers: `export inspect` review warnings are not machine failure; more proof/docs/readback is not production progress unless an active artifact moves.
- evidence_boundary: `newsroom export inspect` is diagnostic; `data\proofs\ymm4_import\<episode_id>\proof.yml` is operator evidence; `docs/HANDOFF.md` and `docs/RUNTIME_STATE.md` are authority docs; runtime DB/export/proof files are not tracked production source.
- next_allowed_work: use the new `newsroom packet add-critical` path only with a real chosen source, then rebuild downstream artifacts and inspect the resulting export.
- prohibited_work: NLMYTGen subprocess/path integration, NotebookLM API automation, Inoreader OAuth, GUI/dashboard, full `.ymmp`, YouTube upload/publishing, destructive cleanup, raw article body or private data in repo.

## Blocked Or Pending

- YMM4 GUI import proof: request authority. Operator must import `data\exports\episode_756343df9853\script.csv` in YMM4 and fill `data\proofs\ymm4_import\episode_756343df9853\proof.yml`.
- Active critical view: capability exists, but `episode_756343df9853` still needs a real critical source selection and rebuild.
- QuoteManifest human_required noise: P1. Do not let it consume P0 unless the active export path is already moving.
- Packet persistence: P1. Current critical-source relation is durable DB input, but full NotebookPacket persistence remains separate.
- VisualIR-to-final-look gap: keep evaluating whether VisualIR changes affect actual YMM4 composition, density, whitespace, and eye flow.

## Standing Cautions

- Do not count proof/docs/readback growth as production value.
- Keep NLMYTGen as schema handoff only: CSV, JSON, Markdown.
- Separate operator creative/GUI authority from machine-verifiable tasks.
- Do not keep expanding docs around an unperformed YMM4 import proof.
- Case-specific runtime evidence can inform generic capability, but it is not the generic capability's authority by itself.

## Improvement Ideas

- Apply `newsroom packet add-critical` to the active story once a real skeptical or opposing source is chosen, then rebuild packet/script/visual/asset/quote/export.
- Tighten QuoteManifest by separating citation-only references from direct quote and screenshot intent.
- Persist NotebookPacket records when operator packet edits must survive rebuilds beyond source classification.
- Reassess VisualIR by final visual effect, not manifest count: composition, density, whitespace, color hierarchy, and eye flow in YMM4.
