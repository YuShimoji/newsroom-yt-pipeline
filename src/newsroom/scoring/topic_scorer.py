from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import UTC, datetime

from newsroom.scoring.competitor_overlap import competitor_ratio
from newsroom.store.models import Article, StoryCluster, TopicScore


@dataclass(frozen=True)
class ArticleScore:
    score_total: float
    components: dict[str, float]


class TopicScorer:
    """Score article candidates and story clusters with a transparent formula.

    The article-level path remains for M1 reports. The cluster-level path
    is the M2 entry point and the basis for the daily shortlist.
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
        return ArticleScore(score_total=_apply_formula(components), components=components)

    def score_cluster(self, cluster: StoryCluster, articles: list[Article]) -> TopicScore:
        if not articles:
            raise ValueError(f"Cluster {cluster.id!r} has no articles to score")

        article_count = len(articles)
        unique_sources = len({article.source_name for article in articles})
        farm_ratio = competitor_ratio(articles)
        has_official = any(article.source_type == "official" for article in articles)
        all_competitor = farm_ratio >= 0.999

        components = {
            "update_potential": min(1.0, math.log(article_count + 1) / math.log(5)),
            "source_diversity": min(1.0, unique_sources / 4.0),
            "uniqueness": max(0.0, 1.0 - farm_ratio),
            "viewer_utility": 0.50,
            "visualizability": 0.40,
            "evidence_strength": 0.70 if has_official else 0.35,
            "copyright_risk": 0.50 if all_competitor else 0.15,
            "content_farm_overlap": farm_ratio,
        }

        return TopicScore(
            cluster_id=cluster.id,
            score_total=_apply_formula(components),
            components={key: round(value, 4) for key, value in components.items()},
            scored_at=datetime.now(UTC).isoformat(),
        )


def _apply_formula(components: dict[str, float]) -> float:
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
    return round(score * 100, 2)
