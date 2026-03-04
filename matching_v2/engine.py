from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from .config import MatchingConfig
from .data_inspector import DataSchemaDetected, inspect_seed_profiles
from .schemas import GuideProfile, TravelerProfile
from .scoring import DimensionBreakdown, score_match


@dataclass(frozen=True)
class RankedGuideResult:
    guide_id: str
    score: float
    strong_match: bool
    breakdown: dict[str, DimensionBreakdown]
    language_overlap: int


def _as_traveler_profile(profile: TravelerProfile | dict[str, Any]) -> TravelerProfile:
    if isinstance(profile, TravelerProfile):
        return profile
    return TravelerProfile(profile)


def _as_guide_profile(profile: GuideProfile | dict[str, Any]) -> GuideProfile:
    if isinstance(profile, GuideProfile):
        return profile
    return GuideProfile(profile)


def find_best_guides(
    traveler: TravelerProfile | dict[str, Any],
    guides: Sequence[GuideProfile | dict[str, Any]],
    top_n: int = 5,
    threshold: float = 0.80,
    config: MatchingConfig | None = None,
    schema_detected: DataSchemaDetected | None = None,
) -> list[RankedGuideResult]:
    if top_n <= 0:
        return []

    schema = schema_detected or inspect_seed_profiles(print_output=False)
    effective_config = config or MatchingConfig(threshold=threshold)
    traveler_profile = _as_traveler_profile(traveler)

    ranked: list[RankedGuideResult] = []
    for index, guide in enumerate(guides):
        guide_profile = _as_guide_profile(guide)
        score_result = score_match(
            traveler=traveler_profile,
            guide=guide_profile,
            config=effective_config,
            schema_detected=schema,
        )
        raw_guide = guide_profile.raw
        guide_id = str(raw_guide.get("id", f"guide_{index}"))
        ranked.append(
            RankedGuideResult(
                guide_id=guide_id,
                score=score_result.score,
                strong_match=score_result.score >= threshold,
                breakdown=score_result.breakdown,
                language_overlap=score_result.language_overlap,
            )
        )

    ranked.sort(
        key=lambda result: (
            -result.score,
            -result.language_overlap,
            result.guide_id,
        )
    )
    return ranked[:top_n]
