from __future__ import annotations

from newsroom.config import SpeakerConfig, SpeakerProfile


DEFAULT_SPEAKER_CONFIG = SpeakerConfig(
    by_format={
        "yukkuri_dialogue": [
            SpeakerProfile(id="reimu", ymm4_name="霊夢", role="聞き役"),
            SpeakerProfile(id="marisa", ymm4_name="魔理沙", role="解説役"),
        ],
        "anchor_narration": [
            SpeakerProfile(id="anchor", ymm4_name="ナレーター", role="進行"),
        ],
    }
)


def speaker_for_index(
    format_name: str,
    segment_index: int,
    config: SpeakerConfig | None = None,
) -> str:
    active = config or DEFAULT_SPEAKER_CONFIG
    profiles = active.by_format.get(format_name)
    if not profiles:
        profiles = DEFAULT_SPEAKER_CONFIG.by_format.get(format_name)
    if not profiles:
        return "ナレーター"
    return profiles[segment_index % len(profiles)].ymm4_name
