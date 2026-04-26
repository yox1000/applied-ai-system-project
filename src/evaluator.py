from dataclasses import dataclass
from typing import Dict, List

try:
    from .recommender import Recommender, UserProfile
except ImportError:
    from recommender import Recommender, UserProfile


@dataclass
class EvaluationCase:
    name: str
    profile: UserProfile
    expected_genre: str
    expected_mood: str
    minimum_confidence: float = 0.45


@dataclass
class EvaluationResult:
    name: str
    passed: bool
    checks: Dict[str, bool]
    top_song: str
    confidence: float


def evaluate_recommender(recommender: Recommender) -> List[EvaluationResult]:
    """Run simple reliability checks against representative user profiles."""
    cases = [
        EvaluationCase("High-energy pop", UserProfile("pop", "happy", 0.9, False), "pop", "happy"),
        EvaluationCase("Chill lofi", UserProfile("lofi", "chill", 0.25, True), "lofi", "chill"),
        EvaluationCase("Intense rock", UserProfile("rock", "intense", 0.85, False), "rock", "intense"),
    ]

    results = []
    for case in cases:
        top = recommender.recommend_with_context(case.profile, k=1)[0]
        checks = {
            "genre_match": top.song.genre.lower() == case.expected_genre.lower(),
            "mood_match": top.song.mood.lower() == case.expected_mood.lower(),
            "confidence_ok": top.confidence >= case.minimum_confidence,
            "has_grounded_context": len(top.retrieved_context) > 0,
        }
        results.append(
            EvaluationResult(
                name=case.name,
                passed=all(checks.values()),
                checks=checks,
                top_song=top.song.title,
                confidence=top.confidence,
            )
        )
    return results


def summarize_evaluation(results: List[EvaluationResult]) -> str:
    passed = sum(1 for result in results if result.passed)
    total = len(results)
    average_confidence = sum(result.confidence for result in results) / total if total else 0.0
    return (
        f"{passed} out of {total} evaluation cases passed; "
        f"average top-result confidence was {average_confidence:.0%}."
    )
