"""Visual planning.

M6.1 component. Translates a ScriptIR plus its NotebookPacket into a
VisualIR whose units cover the four core cards from PROJECT_SPEC.md §14:
source_card, claim_evidence_card, timeline_spine, and takeaway_row. Source
cards are explicit screenshot/source-display intent; citation-only evidence
defaults to local claim/evidence cards. The remaining card types
(version_diff, actor_map, risk_meter, context_stack, quote_screenshot,
neutral_background) stay deferred until later M6 slices. External image
download is intentionally out of scope; only internal information structure
is laid out here.
"""
