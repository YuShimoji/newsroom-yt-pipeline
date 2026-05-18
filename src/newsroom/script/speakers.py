from __future__ import annotations


YUKKURI_SPEAKERS = ("霊夢", "魔理沙")
ANCHOR_SPEAKER = "ナレーター"


def speaker_for_index(format_name: str, segment_index: int) -> str:
    if format_name == "yukkuri_dialogue":
        return YUKKURI_SPEAKERS[segment_index % len(YUKKURI_SPEAKERS)]
    return ANCHOR_SPEAKER
