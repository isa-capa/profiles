"""Algoritmo de matching Guía ↔ Turista.

Diseñado para una etapa 1 basada en reglas con pesos explícitos,
y preparado para evolucionar a una etapa 2 con machine learning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple


@dataclass(frozen=True)
class MatchWeights:
    """Pesos de cada parámetro de matching (deben sumar 1.0)."""

    interests: float = 0.22
    languages: float = 0.18
    location_overlap: float = 0.12
    travel_style: float = 0.10
    activity_level: float = 0.10
    group_preference: float = 0.08
    food_preferences: float = 0.05
    planning_level: float = 0.05
    transport: float = 0.05
    accessibility: float = 0.05

    def as_dict(self) -> Dict[str, float]:
        return {
            "interests": self.interests,
            "languages": self.languages,
            "location_overlap": self.location_overlap,
            "travel_style": self.travel_style,
            "activity_level": self.activity_level,
            "group_preference": self.group_preference,
            "food_preferences": self.food_preferences,
            "planning_level": self.planning_level,
            "transport": self.transport,
            "accessibility": self.accessibility,
        }


@dataclass
class MatchResult:
    guide_id: Any
    traveler_id: Any
    score: float
    is_match: bool
    breakdown: Dict[str, float]


@dataclass
class MatchConfig:
    """Configuración principal del algoritmo de matching."""

    threshold: float = 0.90
    weights: MatchWeights = field(default_factory=MatchWeights)

    def validate(self) -> None:
        total = sum(self.weights.as_dict().values())
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"Los pesos deben sumar 1.0, suma actual: {total}")


class GuideTravelerMatcher:
    """Motor de matching estilo swipe/ranking entre guías y turistas."""

    def __init__(self, config: Optional[MatchConfig] = None):
        self.config = config or MatchConfig()
        self.config.validate()

    @staticmethod
    def _norm_set(values: Optional[Iterable[Any]]) -> Set[str]:
        if not values:
            return set()
        return {str(v).strip().lower() for v in values if str(v).strip()}

    @staticmethod
    def _jaccard(a: Set[str], b: Set[str]) -> float:
        if not a and not b:
            return 1.0
        union = a | b
        if not union:
            return 0.0
        return len(a & b) / len(union)

    @staticmethod
    def _scalar_similarity(a: Optional[Any], b: Optional[Any]) -> float:
        if a is None and b is None:
            return 1.0
        if a is None or b is None:
            return 0.0
        return 1.0 if str(a).strip().lower() == str(b).strip().lower() else 0.0

    def _score_components(self, traveler: Dict[str, Any], guide: Dict[str, Any]) -> Dict[str, float]:
        t = traveler.get("answers", traveler)
        g = guide.get("answers", guide)

        components = {
            "interests": self._jaccard(self._norm_set(t.get("interests")), self._norm_set(g.get("expertiseAreas"))),
            "languages": self._jaccard(self._norm_set(t.get("languages")), self._norm_set(g.get("languages"))),
            "location_overlap": self._jaccard(self._norm_set(t.get("locations")), self._norm_set(g.get("locations"))),
            "travel_style": self._scalar_similarity(t.get("tripType"), g.get("guidingStyle")),
            "activity_level": self._scalar_similarity(t.get("activityLevel"), g.get("tourIntensity")),
            "group_preference": self._scalar_similarity(t.get("groupPreference"), g.get("groupSize")),
            "food_preferences": self._jaccard(self._norm_set(t.get("foodPreferences")), self._norm_set(g.get("foodOptions"))),
            "planning_level": self._scalar_similarity(t.get("planningLevel"), g.get("planningStyle")),
            "transport": self._scalar_similarity(t.get("transportPreference"), g.get("transportOffered")),
            "accessibility": self._jaccard(self._norm_set(t.get("accessibility")), self._norm_set(g.get("accessibilityAdaptations"))),
        }
        return components

    def compute_match(self, traveler: Dict[str, Any], guide: Dict[str, Any]) -> MatchResult:
        breakdown = self._score_components(traveler, guide)
        weights = self.config.weights.as_dict()
        score = sum(breakdown[k] * weights[k] for k in weights)

        return MatchResult(
            guide_id=guide.get("id"),
            traveler_id=traveler.get("id"),
            score=round(score, 4),
            is_match=score >= self.config.threshold,
            breakdown={k: round(v, 4) for k, v in breakdown.items()},
        )

    def rank_guides_for_traveler(
        self,
        traveler: Dict[str, Any],
        guides: Sequence[Dict[str, Any]],
        top_k: Optional[int] = None,
        only_above_threshold: bool = False,
    ) -> List[MatchResult]:
        scored = [self.compute_match(traveler, guide) for guide in guides]
        scored.sort(key=lambda item: item.score, reverse=True)

        if only_above_threshold:
            scored = [item for item in scored if item.is_match]
        if top_k is not None:
            scored = scored[:top_k]
        return scored


class MLMatcherAdapter:
    """Adapter para etapa 2 (Machine Learning).

    Este esqueleto permite reemplazar/fusionar el scoring por reglas con un modelo
    supervisado sin romper el contrato del servicio.
    """

    def __init__(self):
        self.model = None
        self.feature_order: Tuple[str, ...] = (
            "interests",
            "languages",
            "location_overlap",
            "travel_style",
            "activity_level",
            "group_preference",
            "food_preferences",
            "planning_level",
            "transport",
            "accessibility",
        )

    def build_feature_vector(self, rule_breakdown: Dict[str, float]) -> List[float]:
        return [rule_breakdown.get(name, 0.0) for name in self.feature_order]

    def fit(self, X: List[List[float]], y: List[int]) -> None:
        """Entrena un modelo binario de match/no-match.

        Requiere instalar dependencias de ML en etapa 2 (por ejemplo scikit-learn).
        """
        try:
            from sklearn.linear_model import LogisticRegression
        except ImportError as exc:
            raise ImportError(
                "Instala scikit-learn para habilitar entrenamiento ML: pip install scikit-learn"
            ) from exc

        self.model = LogisticRegression(max_iter=400)
        self.model.fit(X, y)

    def predict_proba(self, feature_vector: List[float]) -> float:
        if self.model is None:
            raise RuntimeError("El modelo ML no está entrenado todavía")
        return float(self.model.predict_proba([feature_vector])[0][1])


if __name__ == "__main__":
    traveler = {
        "id": "t-001",
        "answers": {
            "interests": ["cultura", "historia", "gastronomía"],
            "languages": ["español", "inglés"],
            "locations": ["CDMX", "Puebla"],
            "tripType": "cultural",
            "activityLevel": "media",
            "groupPreference": "pequeño",
            "foodPreferences": ["local"],
            "planningLevel": "planificado",
            "transportPreference": "a pie",
            "accessibility": ["rampas"],
        },
    }

    guides = [
        {
            "id": "g-001",
            "answers": {
                "expertiseAreas": ["historia", "cultura", "arte"],
                "languages": ["español", "inglés"],
                "locations": ["CDMX", "Taxco"],
                "guidingStyle": "cultural",
                "tourIntensity": "media",
                "groupSize": "pequeño",
                "foodOptions": ["local", "veg"],
                "planningStyle": "planificado",
                "transportOffered": "a pie",
                "accessibilityAdaptations": ["rampas"],
            },
        },
        {
            "id": "g-002",
            "answers": {
                "expertiseAreas": ["aventura"],
                "languages": ["francés"],
                "locations": ["Cancún"],
                "guidingStyle": "aventura",
                "tourIntensity": "alta",
                "groupSize": "grande",
                "foodOptions": ["internacional"],
                "planningStyle": "flexible",
                "transportOffered": "auto",
                "accessibilityAdaptations": [],
            },
        },
    ]

    matcher = GuideTravelerMatcher(MatchConfig(threshold=0.90))
    ranking = matcher.rank_guides_for_traveler(traveler, guides)

    for result in ranking:
        status = "MATCH ✅" if result.is_match else "Sin match"
        print(f"{result.guide_id} -> score={result.score:.2%} | {status}")
        print(f"breakdown={result.breakdown}\n")
