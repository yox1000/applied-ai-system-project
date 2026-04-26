"""
Command line runner for the RAG-grounded Music Recommender Simulation.
"""

import logging

try:
    from .evaluator import evaluate_recommender, summarize_evaluation
    from .recommender import Recommender, UserProfile, load_song_objects
except ImportError:
    from evaluator import evaluate_recommender, summarize_evaluation
    from recommender import Recommender, UserProfile, load_song_objects


def main() -> None:
    logging.basicConfig(
        filename="recommender.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    songs = load_song_objects("data/songs.csv")
    recommender = Recommender(songs)
    print(f"Loaded songs: {len(songs)}")

    profiles = {
        "High-Energy Pop": UserProfile("pop", "happy", 0.9, likes_acoustic=False),
        "Chill Lofi": UserProfile("lofi", "chill", 0.25, likes_acoustic=True),
        "Deep Intense Rock": UserProfile("rock", "intense", 0.85, likes_acoustic=False),
    }

    for profile_name, user_profile in profiles.items():
        print(f"\n=== {profile_name} ===")
        recommendations = recommender.recommend_with_context(user_profile, k=3)

        if not recommendations:
            print("No recommendations available.")
            continue

        for index, result in enumerate(recommendations, start=1):
            context_titles = ", ".join(song.title for song in result.retrieved_context)
            print(f"{index}. {result.song.title} by {result.song.artist}")
            print(f"   Score: {result.score:.2f}")
            print(f"   Confidence: {result.confidence:.0%}")
            print(f"   Retrieved evidence: {context_titles}")
            print(f"   AI explanation: {result.explanation}")
            print("   " + "-" * 40)

    print("\n=== Reliability Evaluation ===")
    evaluation_results = evaluate_recommender(recommender)
    for result in evaluation_results:
        status = "PASS" if result.passed else "FAIL"
        print(
            f"{status}: {result.name} -> {result.top_song} "
            f"({result.confidence:.0%} confidence, checks={result.checks})"
        )
    print(summarize_evaluation(evaluation_results))


if __name__ == "__main__":
    main()
