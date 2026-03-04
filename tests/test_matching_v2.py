from __future__ import annotations

from pathlib import Path

import pytest

from matching_v2.config import MatchingConfig
from matching_v2.data_inspector import inspect_seed_profiles, load_seed_profiles
from matching_v2.engine import find_best_guides
from matching_v2.mappings import MAP_VALIDATION_ERROR, build_dynamic_mappings
from matching_v2.schemas import GuideProfile, TravelerProfile
from matching_v2.scoring import (
    compute_available_weights,
    ordinal_similarity,
    score_match,
)


SEED_PATH = Path(__file__).resolve().parents[1] / "data" / "seedProfiles.json"


@pytest.fixture(scope="module")
def seed_data() -> dict:
    return load_seed_profiles(SEED_PATH)


@pytest.fixture(scope="module")
def schema():
    return inspect_seed_profiles(SEED_PATH, print_output=False)


def test_inspector_detects_traveler_keys(schema) -> None:
    assert schema.traveler_keys == sorted(
        [
            "accessibility",
            "foodPrefs",
            "groupPreference",
            "interests",
            "languages",
            "notes",
            "pace",
            "photoVibe",
            "planningLevel",
            "transport",
            "travelStyle",
        ]
    )


def test_inspector_detects_guide_keys(schema) -> None:
    assert schema.guide_keys == sorted(
        [
            "accessibility",
            "certs",
            "experienceLevel",
            "expertise",
            "groupSize",
            "guideStyle",
            "languages",
            "locations",
            "notes",
            "pace",
            "photoVibe",
            "transportSupport",
        ]
    )


def test_inspector_detects_categorical_values(schema) -> None:
    assert "Historia" in schema.categorical_values_by_field["interests"]
    assert "Caminar" in schema.categorical_values_by_field["transport"]
    assert "Auto propio" in schema.categorical_values_by_field["transportSupport"]


def test_no_unknown_category_allowed(seed_data, schema) -> None:
    traveler = dict(seed_data["traveler"][0])
    traveler["interests"] = ["Categoria Inventada"]
    traveler_profile = TravelerProfile(traveler)
    guide_profile = GuideProfile(seed_data["guide"][0])

    with pytest.raises(ValueError, match=MAP_VALIDATION_ERROR):
        score_match(traveler_profile, guide_profile, MatchingConfig(), schema)


def test_score_is_always_between_0_and_1(seed_data, schema) -> None:
    traveler_profile = TravelerProfile(seed_data["traveler"][0])
    for raw_guide in seed_data["guide"]:
        guide_profile = GuideProfile(raw_guide)
        result = score_match(traveler_profile, guide_profile, MatchingConfig(), schema)
        assert 0.0 <= result.score <= 1.0


def test_renormalization_excludes_missing_dimension(seed_data, schema) -> None:
    traveler = dict(seed_data["traveler"][0])
    traveler["languages"] = []
    traveler_profile = TravelerProfile(traveler)
    guide_profile = GuideProfile(seed_data["guide"][0])
    result = score_match(traveler_profile, guide_profile, MatchingConfig(), schema)

    total_weight = sum(item.weight for item in result.breakdown.values())
    assert pytest.approx(total_weight, rel=1e-9) == 1.0
    assert "languages" not in result.breakdown


def test_compute_available_weights_renormalizes() -> None:
    base = {"a": 0.5, "b": 0.3, "c": 0.2}
    available = {"a": True, "b": False, "c": True}
    result = compute_available_weights(base, available)

    assert pytest.approx(result["a"], rel=1e-9) == 0.5 / 0.7
    assert pytest.approx(result["c"], rel=1e-9) == 0.2 / 0.7
    assert "b" not in result


def test_ranking_is_sorted_desc(seed_data, schema) -> None:
    ranking = find_best_guides(
        traveler=seed_data["traveler"][0],
        guides=seed_data["guide"],
        top_n=5,
        threshold=0.8,
        schema_detected=schema,
    )
    scores = [item.score for item in ranking]
    assert scores == sorted(scores, reverse=True)


def test_threshold_marks_strong_match(seed_data, schema) -> None:
    ranking = find_best_guides(
        traveler=seed_data["traveler"][0],
        guides=seed_data["guide"],
        top_n=5,
        threshold=1.0,
        schema_detected=schema,
    )
    assert ranking
    assert all(not item.strong_match for item in ranking)


def test_transport_map_uses_only_real_values(schema) -> None:
    mappings = build_dynamic_mappings(schema)
    traveler_transport_allowed = set(schema.traveler_categorical_values["transport"])
    guide_transport_allowed = set(schema.guide_categorical_values["transportSupport"])

    assert set(mappings.transport_map.keys()).issubset(traveler_transport_allowed)
    for mapped_values in mappings.transport_map.values():
        assert set(mapped_values).issubset(guide_transport_allowed)


def test_photo_vibe_ordinal_is_consistent(schema) -> None:
    mappings = build_dynamic_mappings(schema)
    ordered = sorted(mappings.photo_vibe_rank, key=mappings.photo_vibe_rank.get)
    assert ordered
    assert ordinal_similarity(ordered[0], ordered[0], mappings.photo_vibe_rank) == 1.0
    if len(ordered) >= 3:
        low = ordered[0]
        mid = ordered[len(ordered) // 2]
        high = ordered[-1]
        assert ordinal_similarity(low, high, mappings.photo_vibe_rank) <= ordinal_similarity(
            low, mid, mappings.photo_vibe_rank
        )


def test_empty_guide_fields_do_not_break(seed_data, schema) -> None:
    guide = dict(seed_data["guide"][0])
    guide["transportSupport"] = []
    guide["photoVibe"] = ""
    guide["accessibility"] = []

    traveler_profile = TravelerProfile(seed_data["traveler"][0])
    guide_profile = GuideProfile(guide)
    result = score_match(traveler_profile, guide_profile, MatchingConfig(), schema)
    assert 0.0 <= result.score <= 1.0
