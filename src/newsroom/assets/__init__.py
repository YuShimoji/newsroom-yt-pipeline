"""Asset manifest skeleton.

M6.2 component. Suggests asset candidates per VisualUnit, respecting
configs/quote_policy.yml. External URLs always carry approval_state =
human_required (max_unreviewed_external_assets: 0). Automatic download of
external images is intentionally out of scope; this module only proposes
candidates and records approval state.
"""
