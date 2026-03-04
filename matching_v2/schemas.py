from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


JsonDict = dict[str, Any]


def _normalize_to_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    if isinstance(value, (list, tuple, set)):
        normalized: list[str] = []
        for item in value:
            if item is None:
                continue
            stripped = str(item).strip()
            if stripped:
                normalized.append(stripped)
        return normalized
    stripped = str(value).strip()
    return [stripped] if stripped else []


def _normalize_numeric(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            return float(stripped)
        except ValueError:
            return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


@dataclass
class TravelerProfile:
    raw: JsonDict
    interests: list[str] = field(init=False)
    travelStyle: list[str] = field(init=False)
    languages: list[str] = field(init=False)
    pace: float | None = field(init=False)
    groupPreference: list[str] = field(init=False)
    foodPrefs: list[str] = field(init=False)
    planningLevel: float | None = field(init=False)
    transport: list[str] = field(init=False)
    photoVibe: list[str] = field(init=False)
    accessibility: list[str] = field(init=False)

    def __post_init__(self) -> None:
        self.interests = _normalize_to_list(self.raw.get("interests"))
        self.travelStyle = _normalize_to_list(self.raw.get("travelStyle"))
        self.languages = _normalize_to_list(self.raw.get("languages"))
        self.pace = _normalize_numeric(self.raw.get("pace"))
        self.groupPreference = _normalize_to_list(self.raw.get("groupPreference"))
        self.foodPrefs = _normalize_to_list(self.raw.get("foodPrefs"))
        self.planningLevel = _normalize_numeric(self.raw.get("planningLevel"))
        self.transport = _normalize_to_list(self.raw.get("transport"))
        self.photoVibe = _normalize_to_list(self.raw.get("photoVibe"))
        self.accessibility = _normalize_to_list(self.raw.get("accessibility"))


@dataclass
class GuideProfile:
    raw: JsonDict
    expertise: list[str] = field(init=False)
    locations: list[str] = field(init=False)
    experienceLevel: list[str] = field(init=False)
    languages: list[str] = field(init=False)
    guideStyle: list[str] = field(init=False)
    groupSize: list[str] = field(init=False)
    pace: float | None = field(init=False)
    transportSupport: list[str] = field(init=False)
    certs: list[str] = field(init=False)
    accessibility: list[str] = field(init=False)
    photoVibe: list[str] = field(init=False)

    def __post_init__(self) -> None:
        self.expertise = _normalize_to_list(self.raw.get("expertise"))
        self.locations = _normalize_to_list(self.raw.get("locations"))
        self.experienceLevel = _normalize_to_list(self.raw.get("experienceLevel"))
        self.languages = _normalize_to_list(self.raw.get("languages"))
        self.guideStyle = _normalize_to_list(self.raw.get("guideStyle"))
        self.groupSize = _normalize_to_list(self.raw.get("groupSize"))
        self.pace = _normalize_numeric(self.raw.get("pace"))
        self.transportSupport = _normalize_to_list(self.raw.get("transportSupport"))
        self.certs = _normalize_to_list(self.raw.get("certs"))
        self.accessibility = _normalize_to_list(self.raw.get("accessibility"))
        self.photoVibe = _normalize_to_list(self.raw.get("photoVibe"))
