from __future__ import annotations

import argparse
from pathlib import Path

from .data_inspector import inspect_seed_profiles, load_seed_profiles
from .engine import find_best_guides


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Traveler <-> Guide matching v2")
    parser.add_argument("--traveler-index", type=int, default=0)
    parser.add_argument("--top-n", type=int, default=5)
    parser.add_argument("--threshold", type=float, default=0.80)
    parser.add_argument("--seed-path", type=str, default=None)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    seed_path = Path(args.seed_path) if args.seed_path else None

    schema = inspect_seed_profiles(seed_path=seed_path, print_output=True)
    seed_data = load_seed_profiles(seed_path=seed_path)
    travelers = seed_data.get("traveler", [])
    guides = seed_data.get("guide", [])

    if not isinstance(travelers, list) or not isinstance(guides, list):
        raise ValueError("seedProfiles.json must contain 'traveler' and 'guide' arrays")
    if not travelers:
        raise ValueError("No traveler profiles found")
    if not guides:
        raise ValueError("No guide profiles found")
    if args.traveler_index < 0 or args.traveler_index >= len(travelers):
        raise IndexError(f"Traveler index out of range: {args.traveler_index}")

    traveler = travelers[args.traveler_index]
    ranking = find_best_guides(
        traveler=traveler,
        guides=guides,
        top_n=args.top_n,
        threshold=args.threshold,
        schema_detected=schema,
    )

    print("=== MATCH RANKING ===")
    for position, result in enumerate(ranking, start=1):
        print(f"#{position} Guide ID: {result.guide_id}")
        print(f"Overall score: {result.score:.4f}")
        print(f"Strong match?: {'Yes' if result.strong_match else 'No'}")
        print("Breakdown:")
        for dimension, detail in result.breakdown.items():
            print(
                f"  - {dimension}: score={detail.score:.4f}, "
                f"weight={detail.weight:.4f}, weighted={detail.weighted_score:.4f}"
            )
            print(f"    explanation: {detail.explanation}")
        print("")


if __name__ == "__main__":
    main()
