"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from .recommender import load_songs, recommend_songs
except ImportError:
    from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Define multiple test profiles
    profiles = {
        "High-Energy Pop": {
            "genre": "pop",
            "energy": 0.9,
            "mood": "happy"
        },
        "Chill Lofi": {
            "genre": "lofi",
            "energy": 0.2,
            "mood": "calm"
        },
        "Deep Intense Rock": {
            "genre": "rock",
            "energy": 0.8,
            "mood": "intense"
        }
    }

    # Run recommender for each profile
    for profile_name, user_prefs in profiles.items():
        print(f"\n=== {profile_name} ===")

        recommendations = recommend_songs(user_prefs, songs, k=5)

        if not recommendations:
            print("No recommendations available.")
            continue

        for index, (song, score, explanation) in enumerate(recommendations, start=1):
            print(f"{index}. {song['title']} by {song['artist']}")
            print(f"   Score: {score:.2f}")
            print(f"   Reasons: {explanation}")
            print("   " + "-" * 40)


if __name__ == "__main__":
    main()