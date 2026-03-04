"""Matching Traveler <-> Guide v2 package."""

from .config import MatchingConfig
from .data_inspector import DataSchemaDetected, inspect_seed_profiles, load_seed_profiles
from .engine import RankedGuideResult, find_best_guides
from .schemas import GuideProfile, TravelerProfile
from .scoring import MatchScoreResult, score_match

__all__ = [
    "DataSchemaDetected",
    "GuideProfile",
    "MatchScoreResult",
    "MatchingConfig",
    "RankedGuideResult",
    "TravelerProfile",
    "find_best_guides",
    "inspect_seed_profiles",
    "load_seed_profiles",
    "score_match",
]
