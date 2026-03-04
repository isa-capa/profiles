from __future__ import annotations

from dataclasses import dataclass, field


BASE_WEIGHTS: dict[str, float] = {
    "interests_expertise": 0.30,
    "languages": 0.20,
    "pace": 0.15,
    "group": 0.10,
    "transport": 0.10,
    "photoVibe": 0.10,
    "accessibility": 0.05,
}


DEFAULT_THRESHOLD = 0.80
DEFAULT_MAX_DIFF_PACE = 10.0


@dataclass(frozen=True)
class MatchingConfig:
    base_weights: dict[str, float] = field(default_factory=lambda: dict(BASE_WEIGHTS))
    threshold: float = DEFAULT_THRESHOLD
    max_diff_pace: float = DEFAULT_MAX_DIFF_PACE
