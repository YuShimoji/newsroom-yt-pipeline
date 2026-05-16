from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class NotebookPacket:
    id: str
    story_cluster_id: str
    primary_sources: list[str] = field(default_factory=list)
    news_sources: list[str] = field(default_factory=list)
    critical_views: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)


class NotebookPacketBuilder:
    """M3 interface placeholder.

    M1 creates the stable module boundary only. Packet generation is not
    implemented until after article ledger, clustering, and scoring stabilize.
    """

    def build(self, story_cluster_id: str) -> NotebookPacket:
        raise NotImplementedError(
            f"Notebook packet generation is deferred to M3: {story_cluster_id}"
        )

