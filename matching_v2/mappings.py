from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
import re
from typing import Iterable, Mapping, Sequence

from .data_inspector import DataSchemaDetected


MAP_VALIDATION_ERROR = "Attempted to map category not present in seedProfiles.json"


def _tokenize(value: str) -> set[str]:
    return set(re.findall(r"\w+", value.lower(), flags=re.UNICODE))


def _token_similarity(a: str, b: str) -> float:
    a_tokens = _tokenize(a)
    b_tokens = _tokenize(b)
    if not a_tokens and not b_tokens:
        return 1.0
    if not a_tokens or not b_tokens:
        return 0.0
    return len(a_tokens & b_tokens) / len(a_tokens | b_tokens)


def _string_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _extract_numbers(value: str) -> set[int]:
    return {int(number) for number in re.findall(r"\d+", value)}


def _numeric_overlap(a: str, b: str) -> bool:
    a_numbers = _extract_numbers(a)
    b_numbers = _extract_numbers(b)
    return bool(a_numbers and b_numbers and (a_numbers & b_numbers))


def _build_overlap_map(source_values: Sequence[str], target_values: Sequence[str]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    normalized_targets = sorted(set(target_values))
    for source in sorted(set(source_values)):
        scored_matches: list[tuple[float, str]] = []
        for target in normalized_targets:
            token_score = _token_similarity(source, target)
            fuzzy_score = _string_similarity(source, target)
            numeric_bonus = 1.0 if _numeric_overlap(source, target) else 0.0
            score = max(token_score, fuzzy_score * 0.70, numeric_bonus)
            if score >= 0.34:
                scored_matches.append((score, target))

        scored_matches.sort(key=lambda item: (-item[0], item[1]))
        if scored_matches:
            top_score = scored_matches[0][0]
            selected = [target for score, target in scored_matches if score >= top_score - 0.10]
            mapping[source] = sorted(set(selected))
        else:
            mapping[source] = []
    return mapping


def _build_ordinal_rank(values: Iterable[str]) -> dict[str, int]:
    ordered = sorted(set(values), key=lambda value: value.lower())
    return {value: index for index, value in enumerate(ordered)}


def _ensure_in_allowed(values: Iterable[str], allowed_values: set[str]) -> None:
    for value in values:
        if value not in allowed_values:
            raise ValueError(MAP_VALIDATION_ERROR)


def _validate_mapping_entries(
    mapping: Mapping[str, Sequence[str]],
    source_allowed: set[str],
    target_allowed: set[str],
) -> None:
    for source, targets in mapping.items():
        if source not in source_allowed:
            raise ValueError(MAP_VALIDATION_ERROR)
        for target in targets:
            if target not in target_allowed:
                raise ValueError(MAP_VALIDATION_ERROR)


@dataclass(frozen=True)
class DynamicMappings:
    interests_expertise_map: dict[str, list[str]]
    transport_map: dict[str, list[str]]
    group_map: dict[str, list[str]]
    photo_vibe_rank: dict[str, int]
    traveler_allowed: dict[str, set[str]]
    guide_allowed: dict[str, set[str]]


def validate_mapping_against_schema(mappings: DynamicMappings, schema: DataSchemaDetected) -> None:
    traveler_allowed = {
        field: set(values) for field, values in schema.traveler_categorical_values.items()
    }
    guide_allowed = {
        field: set(values) for field, values in schema.guide_categorical_values.items()
    }

    _validate_mapping_entries(
        mappings.interests_expertise_map,
        traveler_allowed.get("interests", set()),
        guide_allowed.get("expertise", set()),
    )
    _validate_mapping_entries(
        mappings.transport_map,
        traveler_allowed.get("transport", set()),
        guide_allowed.get("transportSupport", set()),
    )
    _validate_mapping_entries(
        mappings.group_map,
        traveler_allowed.get("groupPreference", set()),
        guide_allowed.get("groupSize", set()),
    )

    photo_values_allowed = set(schema.categorical_values_by_field.get("photoVibe", []))
    _ensure_in_allowed(mappings.photo_vibe_rank.keys(), photo_values_allowed)


def build_dynamic_mappings(schema: DataSchemaDetected) -> DynamicMappings:
    traveler_allowed = {
        field: set(values) for field, values in schema.traveler_categorical_values.items()
    }
    guide_allowed = {
        field: set(values) for field, values in schema.guide_categorical_values.items()
    }

    interests_map = _build_overlap_map(
        schema.traveler_categorical_values.get("interests", []),
        schema.guide_categorical_values.get("expertise", []),
    )
    transport_map = _build_overlap_map(
        schema.traveler_categorical_values.get("transport", []),
        schema.guide_categorical_values.get("transportSupport", []),
    )
    group_map = _build_overlap_map(
        schema.traveler_categorical_values.get("groupPreference", []),
        schema.guide_categorical_values.get("groupSize", []),
    )

    photo_values = schema.categorical_values_by_field.get("photoVibe", [])
    photo_vibe_rank = _build_ordinal_rank(photo_values)

    detected_mappings = DynamicMappings(
        interests_expertise_map=interests_map,
        transport_map=transport_map,
        group_map=group_map,
        photo_vibe_rank=photo_vibe_rank,
        traveler_allowed=traveler_allowed,
        guide_allowed=guide_allowed,
    )
    validate_mapping_against_schema(detected_mappings, schema)
    return detected_mappings


def expand_mapped_values(
    source_values: Sequence[str],
    mapping: Mapping[str, Sequence[str]],
    allowed_source_values: set[str],
) -> set[str]:
    expanded: set[str] = set()
    for value in source_values:
        if value not in allowed_source_values:
            raise ValueError(MAP_VALIDATION_ERROR)
        expanded.update(mapping.get(value, []))
    return expanded
