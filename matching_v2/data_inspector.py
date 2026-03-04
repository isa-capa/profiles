from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


JsonDict = dict[str, Any]


@dataclass(frozen=True)
class DataSchemaDetected:
    traveler_keys: list[str]
    guide_keys: list[str]
    traveler_categorical_values: dict[str, list[str]]
    guide_categorical_values: dict[str, list[str]]
    categorical_values_by_field: dict[str, list[str]]


def _default_seed_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "seedProfiles.json"


def load_seed_profiles(seed_path: str | Path | None = None) -> JsonDict:
    path = Path(seed_path) if seed_path is not None else _default_seed_path()
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("seedProfiles.json must contain a JSON object at root level")
    return data


def _collect_role_data(profiles: list[Any]) -> tuple[set[str], dict[str, list[Any]]]:
    keys: set[str] = set()
    observed_values: dict[str, list[Any]] = {}

    for profile in profiles:
        if not isinstance(profile, dict):
            continue
        for field, value in profile.items():
            keys.add(field)
            observed_values.setdefault(field, []).append(value)

    return keys, observed_values


def _is_categorical_field(values: list[Any]) -> bool:
    saw_textual = False
    for value in values:
        if value is None:
            continue
        if isinstance(value, str):
            saw_textual = True
            continue
        if isinstance(value, (list, tuple, set)):
            if all(item is None or isinstance(item, str) for item in value):
                saw_textual = True
                continue
            return False
        return False
    return saw_textual


def _extract_unique_categorical_values(values: list[Any]) -> list[str]:
    unique_values: set[str] = set()
    for value in values:
        if isinstance(value, str):
            normalized = value.strip()
            if normalized:
                unique_values.add(normalized)
            continue
        if isinstance(value, (list, tuple, set)):
            for item in value:
                if item is None:
                    continue
                normalized = str(item).strip()
                if normalized:
                    unique_values.add(normalized)
    return sorted(unique_values)


def _categorical_values_for_role(observed_values: dict[str, list[Any]]) -> dict[str, list[str]]:
    detected: dict[str, list[str]] = {}
    for field, values in observed_values.items():
        if _is_categorical_field(values):
            detected[field] = _extract_unique_categorical_values(values)
    return detected


def detect_schema(seed_data: JsonDict) -> DataSchemaDetected:
    travelers_raw = seed_data.get("traveler", [])
    guides_raw = seed_data.get("guide", [])

    travelers = travelers_raw if isinstance(travelers_raw, list) else []
    guides = guides_raw if isinstance(guides_raw, list) else []

    traveler_keys, traveler_values = _collect_role_data(travelers)
    guide_keys, guide_values = _collect_role_data(guides)

    traveler_categorical_values = _categorical_values_for_role(traveler_values)
    guide_categorical_values = _categorical_values_for_role(guide_values)

    merged_fields = set(traveler_categorical_values) | set(guide_categorical_values)
    merged_categorical_values: dict[str, list[str]] = {}
    for field in sorted(merged_fields):
        merged_values = set(traveler_categorical_values.get(field, []))
        merged_values.update(guide_categorical_values.get(field, []))
        merged_categorical_values[field] = sorted(merged_values)

    return DataSchemaDetected(
        traveler_keys=sorted(traveler_keys),
        guide_keys=sorted(guide_keys),
        traveler_categorical_values=traveler_categorical_values,
        guide_categorical_values=guide_categorical_values,
        categorical_values_by_field=merged_categorical_values,
    )


def print_detected_schema(schema: DataSchemaDetected) -> None:
    print("=== DETECTED TRAVELER KEYS ===")
    print(json.dumps(schema.traveler_keys, ensure_ascii=False))
    print("=== DETECTED GUIDE KEYS ===")
    print(json.dumps(schema.guide_keys, ensure_ascii=False))

    for field in sorted(schema.categorical_values_by_field):
        print(f"=== DETECTED VALUES: {field} ===")
        print(json.dumps(schema.categorical_values_by_field[field], ensure_ascii=False))


def inspect_seed_profiles(
    seed_path: str | Path | None = None,
    print_output: bool = True,
) -> DataSchemaDetected:
    seed_data = load_seed_profiles(seed_path=seed_path)
    schema = detect_schema(seed_data)
    if print_output:
        print_detected_schema(schema)
    return schema
