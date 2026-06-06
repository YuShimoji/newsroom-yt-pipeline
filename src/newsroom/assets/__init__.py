"""Asset / quote manifest skeletons.

M6.2 suggests asset candidates per VisualUnit, respecting
configs/quote_policy.yml. M6.3 adds QuoteManifest rows for citation-only
source refs, direct quote/data-use intent, and source-card screenshots.
External screenshot URLs always carry approval_state = human_required.
Automatic download of external images is intentionally out of scope; this
module only proposes candidates and records approval state.
"""
