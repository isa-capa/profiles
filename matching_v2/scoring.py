from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .config import MatchingConfig
from .data_inspector import DataSchemaDetected
from .mappings import build_dynamic_mappings, expand_mapped_values
from .schemas import GuideProfile, TravelerProfile


def _to_set(values: Iterable[str]) -> set[str]:
    return {value for value in values if value}


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, value))


def jaccard_similarity(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return _clamp_01(len(a & b) / len(a | b))


def numeric_similarity(a: float | None, b: float | None, max_diff: float) -> float:
    if a is None or b is None:
        return 0.0
    if max_diff <= 0:
        return 1.0 if a == b else 0.0
    diff = abs(a - b)
    return _clamp_01(1.0 - min(diff, max_diff) / max_diff)


def ordinal_similarity(a: str | None, b: str | None, rank_map: dict[str, int]) -> float:
    if not a or not b:
        return 0.0
    if a not in rank_map or b not in rank_map:
        return 0.0
    max_rank = max(rank_map.values(), default=0)
    if max_rank == 0:
        return 1.0
    diff = abs(rank_map[a] - rank_map[b]) / max_rank
    return _clamp_01(1.0 - diff)


def categorical_score(
    traveler_values: Iterable[str],
    guide_values: Iterable[str],
    mapping: dict[str, list[str]] | None = None,
    allowed_source_values: set[str] | None = None,
) -> float:
    traveler_set = _to_set(traveler_values)
    guide_set = _to_set(guide_values)

    if mapping is not None:
        allowed = allowed_source_values if allowed_source_values is not None else set(mapping.keys())
        expanded = expand_mapped_values(sorted(traveler_set), mapping, allowed)
        if expanded:
            return jaccard_similarity(expanded, guide_set)
    return jaccard_similarity(traveler_set, guide_set)


def compute_available_weights(
    base_weights: dict[str, float],
    available_dimensions: dict[str, bool],
) -> dict[str, float]:
    active_weights = {
        dimension: weight
        for dimension, weight in base_weights.items()
        if available_dimensions.get(dimension, False)
    }
    total_weight = sum(active_weights.values())
    if total_weight <= 0:
        return {}
    return {
        dimension: weight / total_weight for dimension, weight in active_weights.items()
    }


def _categorical_explanation(
    title: str,
    score: float,
    traveler_values: set[str],
    guide_values: set[str],
) -> str:
    overlap = traveler_values & guide_values
    return (
        f"{title}: score={score:.2f}, coincidencias directas={len(overlap)} "
        f"de {len(traveler_values)} vs {len(guide_values)}"
    )


@dataclass(frozen=True)
class DimensionBreakdown:
    score: float
    weight: float
    weighted_score: float
    explanation: str


@dataclass(frozen=True)
class MatchScoreResult:
    score: float
    breakdown: dict[str, DimensionBreakdown]
    language_overlap: int


def score_match(
    traveler: TravelerProfile,
    guide: GuideProfile,
    config: MatchingConfig,
    schema_detected: DataSchemaDetected,
) -> MatchScoreResult:
    mappings = build_dynamic_mappings(schema_detected)

    available_dimensions = {
        "interests_expertise": bool(traveler.interests and guide.expertise),
        "languages": bool(traveler.languages and guide.languages),
        "pace": traveler.pace is not None and guide.pace is not None,
        "group": bool(traveler.groupPreference and guide.groupSize),
        "transport": bool(traveler.transport and guide.transportSupport),
        "photoVibe": bool(traveler.photoVibe and guide.photoVibe),
        "accessibility": bool(traveler.accessibility and guide.accessibility),
    }
    weights = compute_available_weights(config.base_weights, available_dimensions)

    raw_scores: dict[str, float] = {}
    explanations: dict[str, str] = {}

    if available_dimensions["interests_expertise"]:
        raw_scores["interests_expertise"] = categorical_score(
            traveler.interests,
            guide.expertise,
            mapping=mappings.interests_expertise_map,
            allowed_source_values=mappings.traveler_allowed.get("interests", set()),
        )
        explanations["interests_expertise"] = _categorical_explanation(
            "Intereses/experiencia",
            raw_scores["interests_expertise"],
            _to_set(traveler.interests),
            _to_set(guide.expertise),
        )

    if available_dimensions["languages"]:
        language_set_traveler = _to_set(traveler.languages)
        language_set_guide = _to_set(guide.languages)
        raw_scores["languages"] = jaccard_similarity(language_set_traveler, language_set_guide)
        overlap = len(language_set_traveler & language_set_guide)
        explanations["languages"] = (
            f"Idiomas: score={raw_scores['languages']:.2f}, "
            f"coincidencias={overlap}"
        )

    if available_dimensions["pace"]:
        raw_scores["pace"] = numeric_similarity(traveler.pace, guide.pace, config.max_diff_pace)
        pace_diff = abs((traveler.pace or 0.0) - (guide.pace or 0.0))
        explanations["pace"] = (
            f"Ritmo: score={raw_scores['pace']:.2f}, diferencia={pace_diff:.1f}"
        )

    if available_dimensions["group"]:
        raw_scores["group"] = categorical_score(
            traveler.groupPreference,
            guide.groupSize,
            mapping=mappings.group_map,
            allowed_source_values=mappings.traveler_allowed.get("groupPreference", set()),
        )
        explanations["group"] = _categorical_explanation(
            "Grupo",
            raw_scores["group"],
            _to_set(traveler.groupPreference),
            _to_set(guide.groupSize),
        )

    if available_dimensions["transport"]:
        raw_scores["transport"] = categorical_score(
            traveler.transport,
            guide.transportSupport,
            mapping=mappings.transport_map,
            allowed_source_values=mappings.traveler_allowed.get("transport", set()),
        )
        explanations["transport"] = _categorical_explanation(
            "Transporte",
            raw_scores["transport"],
            _to_set(traveler.transport),
            _to_set(guide.transportSupport),
        )

    if available_dimensions["photoVibe"]:
        traveler_photo = traveler.photoVibe[0] if traveler.photoVibe else None
        guide_photo = guide.photoVibe[0] if guide.photoVibe else None
        raw_scores["photoVibe"] = ordinal_similarity(
            traveler_photo,
            guide_photo,
            mappings.photo_vibe_rank,
        )
        explanations["photoVibe"] = (
            f"Photo vibe: score={raw_scores['photoVibe']:.2f}, "
            f"viajero={traveler_photo}, guia={guide_photo}"
        )

    if available_dimensions["accessibility"]:
        traveler_access = _to_set(traveler.accessibility)
        guide_access = _to_set(guide.accessibility)
        raw_scores["accessibility"] = jaccard_similarity(traveler_access, guide_access)
        explanations["accessibility"] = _categorical_explanation(
            "Accesibilidad",
            raw_scores["accessibility"],
            traveler_access,
            guide_access,
        )

    breakdown: dict[str, DimensionBreakdown] = {}
    total_score = 0.0
    for dimension, raw_score in raw_scores.items():
        weight = weights.get(dimension, 0.0)
        weighted_score = raw_score * weight
        total_score += weighted_score
        breakdown[dimension] = DimensionBreakdown(
            score=_clamp_01(raw_score),
            weight=weight,
            weighted_score=_clamp_01(weighted_score),
            explanation=explanations.get(dimension, ""),
        )

    language_overlap = len(_to_set(traveler.languages) & _to_set(guide.languages))
    return MatchScoreResult(
        score=_clamp_01(total_score),
        breakdown=breakdown,
        language_overlap=language_overlap,
    )
