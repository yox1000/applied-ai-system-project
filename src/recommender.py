import csv
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs from a CSV file and return them as dictionaries."""
    path = Path(csv_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent.parent / path

    songs: List[Dict] = []
    with path.open(newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against the user's preference profile."""
    def get_pref(*keys, default=None):
        for key in keys:
            if key in user_prefs:
                return user_prefs[key]
        return default

    def proximity_score(value: float, target: float, tolerance: float) -> float:
        if tolerance <= 0:
            return 0.0
        diff = abs(value - target)
        return max(0.0, 1.0 - diff / tolerance)

    genre_pref = get_pref("favorite_genre", "genre")
    mood_pref = get_pref("favorite_mood", "mood")
    target_energy = float(get_pref("target_energy", "energy", default=0.5))
    target_tempo = float(get_pref("target_tempo_bpm", "tempo_bpm", default=100.0))
    target_valence = float(get_pref("target_valence", "valence", default=0.5))
    target_danceability = float(get_pref("target_danceability", "danceability", default=0.5))
    target_acousticness = float(get_pref("target_acousticness", "acousticness", default=0.5))

    energy_tolerance = float(get_pref("energy_tolerance", default=0.20))
    tempo_tolerance = float(get_pref("tempo_tolerance", default=20.0))
    valence_tolerance = float(get_pref("valence_tolerance", default=0.20))
    danceability_tolerance = float(get_pref("danceability_tolerance", default=0.20))
    acousticness_tolerance = float(get_pref("acousticness_tolerance", default=0.25))

    weights = {
        "genre": 1.0,
        "mood": 1.7,
        "energy": 2.0,
        "tempo_bpm": 0.8,
        "valence": 0.7,
        "danceability": 0.6,
        "acousticness": 0.9,
    }

    score = 0.0
    reasons: List[str] = []

    if genre_pref is not None and str(song.get("genre", "")).strip().lower() == str(genre_pref).strip().lower():
        score += weights["genre"]
        reasons.append(f"genre match (+{weights['genre']:.1f})")

    if mood_pref is not None and str(song.get("mood", "")).strip().lower() == str(mood_pref).strip().lower():
        score += weights["mood"]
        reasons.append(f"mood match (+{weights['mood']:.1f})")

    energy_score = proximity_score(song["energy"], target_energy, energy_tolerance)
    energy_points = energy_score * weights["energy"]
    if energy_points > 0:
        score += energy_points
        reasons.append(f"energy close to {target_energy:.2f} (+{energy_points:.2f})")

    tempo_score = proximity_score(song["tempo_bpm"], target_tempo, tempo_tolerance)
    tempo_points = tempo_score * weights["tempo_bpm"]
    if tempo_points > 0:
        score += tempo_points
        reasons.append(f"tempo close to {target_tempo:.0f} BPM (+{tempo_points:.2f})")

    valence_score = proximity_score(song["valence"], target_valence, valence_tolerance)
    valence_points = valence_score * weights["valence"]
    if valence_points > 0:
        score += valence_points
        reasons.append(f"valence close to {target_valence:.2f} (+{valence_points:.2f})")

    danceability_score = proximity_score(song["danceability"], target_danceability, danceability_tolerance)
    danceability_points = danceability_score * weights["danceability"]
    if danceability_points > 0:
        score += danceability_points
        reasons.append(f"danceability close to {target_danceability:.2f} (+{danceability_points:.2f})")

    acousticness_score = proximity_score(song["acousticness"], target_acousticness, acousticness_tolerance)
    acousticness_points = acousticness_score * weights["acousticness"]
    if acousticness_points > 0:
        score += acousticness_points
        reasons.append(f"acousticness close to {target_acousticness:.2f} (+{acousticness_points:.2f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Rank all songs by score and return the top K recommendations."""
    scored_songs = [
        (song, *score_song(user_prefs, song))
        for song in songs
    ]

    ranked_songs = sorted(scored_songs, key=lambda item: item[1], reverse=True)
    top_songs = ranked_songs[:k]

    return [
        (song, score, "; ".join(reasons) if reasons else "No matching reasons")
        for song, score, reasons in top_songs
    ]
