from __future__ import annotations

from dataclasses import dataclass

from newsroom.store.models import EpisodePlan, NotebookPacket, ScriptIR


@dataclass(frozen=True)
class CritiqueFinding:
    guard: str
    severity: str
    message: str


class ScriptCritic:
    """Run the seven editorial guards from PROJECT_SPEC.md §12.4.

    Each guard returns a CritiqueFinding with severity ok / warn / fail
    so the operator review file can show a checklist rather than a yes/no
    verdict. Guards that require natural-language understanding stay as
    'warn' and surface the heuristic signal we can compute now.
    """

    def critique(
        self,
        script: ScriptIR,
        plan: EpisodePlan,
        packet: NotebookPacket,
    ) -> list[CritiqueFinding]:
        return [
            self._guard_factual_sources(script),
            self._guard_speculation_vs_fact(script),
            self._guard_not_article_readout(script, packet),
            self._guard_analysis_over_quote(script),
            self._guard_viewer_utility(plan),
            self._guard_critical_view(script, packet),
            self._guard_visual_density(script, plan),
        ]

    def _guard_factual_sources(self, script: ScriptIR) -> CritiqueFinding:
        offenders = [
            segment.id
            for segment in script.segments
            if segment.claim_type == "fact" and not segment.source_refs
        ]
        if not offenders:
            return CritiqueFinding(
                guard="factual_sources",
                severity="ok",
                message="Every fact-typed segment carries at least one source_ref.",
            )
        return CritiqueFinding(
            guard="factual_sources",
            severity="fail",
            message=f"Fact segments missing source_refs: {offenders}",
        )

    def _guard_speculation_vs_fact(self, script: ScriptIR) -> CritiqueFinding:
        claim_types = {segment.claim_type for segment in script.segments}
        if "fact" in claim_types and "speculation" not in claim_types and "interpretation" in claim_types:
            return CritiqueFinding(
                guard="speculation_vs_fact",
                severity="warn",
                message="No segments are explicitly marked speculation; verify interpretation segments are not hidden speculation.",
            )
        return CritiqueFinding(
            guard="speculation_vs_fact",
            severity="ok",
            message="Fact and speculation tracks are distinguishable by claim_type.",
        )

    def _guard_not_article_readout(
        self, script: ScriptIR, packet: NotebookPacket
    ) -> CritiqueFinding:
        article_titles = [ref.title for ref in packet.primary_sources + packet.news_sources]
        flagged: list[str] = []
        for segment in script.segments:
            for title in article_titles:
                if title and title in segment.text:
                    flagged.append(segment.id)
                    break
        if not flagged:
            return CritiqueFinding(
                guard="not_article_readout",
                severity="ok",
                message="No segment text mirrors a source article title verbatim.",
            )
        return CritiqueFinding(
            guard="not_article_readout",
            severity="warn",
            message=f"Segments whose text echoes a source title: {flagged}",
        )

    def _guard_analysis_over_quote(self, script: ScriptIR) -> CritiqueFinding:
        interpretation = sum(1 for s in script.segments if s.claim_type == "interpretation")
        fact = sum(1 for s in script.segments if s.claim_type == "fact")
        if interpretation == 0:
            return CritiqueFinding(
                guard="analysis_over_quote",
                severity="fail",
                message="Script has no interpretation segments; analysis must lead the script.",
            )
        if interpretation < fact:
            return CritiqueFinding(
                guard="analysis_over_quote",
                severity="warn",
                message=f"Interpretation segments ({interpretation}) outnumbered by fact segments ({fact}); confirm analysis remains primary.",
            )
        return CritiqueFinding(
            guard="analysis_over_quote",
            severity="ok",
            message=f"Interpretation count ({interpretation}) meets or exceeds fact count ({fact}).",
        )

    def _guard_viewer_utility(self, plan: EpisodePlan) -> CritiqueFinding:
        if plan.viewer_utility.strip():
            return CritiqueFinding(
                guard="viewer_utility",
                severity="ok",
                message=f"viewer_utility set: {plan.viewer_utility}",
            )
        return CritiqueFinding(
            guard="viewer_utility",
            severity="fail",
            message="EpisodePlan.viewer_utility is empty.",
        )

    def _guard_critical_view(
        self, script: ScriptIR, packet: NotebookPacket
    ) -> CritiqueFinding:
        if packet.critical_views:
            return CritiqueFinding(
                guard="critical_view",
                severity="ok",
                message=f"Packet provides {len(packet.critical_views)} critical-view source(s).",
            )
        conflict_segments = [
            segment.id
            for segment in script.segments
            if "conflict" in segment.chapter_id
        ]
        if conflict_segments:
            return CritiqueFinding(
                guard="critical_view",
                severity="warn",
                message="Packet has no critical_views; conflict chapter segments need manual critical input.",
            )
        return CritiqueFinding(
            guard="critical_view",
            severity="fail",
            message="No critical view in packet and no conflict chapter in script.",
        )

    def _guard_visual_density(
        self, script: ScriptIR, plan: EpisodePlan
    ) -> CritiqueFinding:
        with_visual = sum(1 for s in script.segments if s.visual_refs)
        if not script.segments:
            return CritiqueFinding(
                guard="visual_density",
                severity="fail",
                message="Script has zero segments.",
            )
        ratio = with_visual / len(script.segments)
        if ratio >= 0.8:
            return CritiqueFinding(
                guard="visual_density",
                severity="ok",
                message=f"{with_visual}/{len(script.segments)} segments carry a visual_ref.",
            )
        return CritiqueFinding(
            guard="visual_density",
            severity="warn",
            message=f"Only {with_visual}/{len(script.segments)} segments have visual_refs; aim for >= 80%.",
        )
