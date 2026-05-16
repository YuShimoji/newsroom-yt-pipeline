from __future__ import annotations

from dataclasses import dataclass

from newsroom.store.models import Article


@dataclass(frozen=True)
class ArticleScore:
    score_total: float
    components: dict[str, float]


class TopicScorer:
    """Transparent placeholder scorer for M1 reports.

    Story-level scoring belongs to M2. M1 exposes a stable interface and visible
    components so reports do not hide that the score is provisional.
    """

    def score_article(self, article: Article) -> ArticleScore:
        components = {
            "update_potential": 0.50,
            "source_diversity": 0.30,
            "uniqueness": 0.40,
            "viewer_utility": 0.45,
            "visualizability": 0.40,
            "evidence_strength": 0.60 if article.source_type == "official" else 0.35,
            "copyright_risk": 0.15,
            "content_farm_overlap": 0.10 if article.source_type == "competitor" else 0.00,
        }
        score = (
            0.25 * components["update_potential"]
            + 0.20 * components["source_diversity"]
            + 0.15 * components["uniqueness"]
            + 0.15 * components["viewer_utility"]
            + 0.10 * components["visualizability"]
            + 0.10 * components["evidence_strength"]
            - 0.15 * components["copyright_risk"]
            - 0.10 * components["content_farm_overlap"]
        )
        return ArticleScore(score_total=round(score * 100, 2), components=components)

