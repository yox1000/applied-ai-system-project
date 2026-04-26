import csv
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

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

    def to_preferences(self) -> Dict:
        """Convert the typed profile into the dictionary shape used by scoring."""
        return {
            "favorite_genre": self.favorite_genre,
            "favorite_mood": self.favorite_mood,
            "target_energy": self.target_energy,
            "target_acousticness": 0.8 if self.likes_acoustic else 0.2,
        }


@dataclass
class RecommendationResult:
    song: Song
    score: float
    confidence: float
    retrieved_context: List[Song]
    explanation: str


logger = logging.getLogger(__name__)

class Recommender:
    """
    OOP implementation of the recommendation logic.

    This class includes the project's integrated RAG-style workflow:
    it retrieves similar catalog songs as evidence, ranks songs with
    the existing scoring rules, and generates explanations grounded in
    the retrieved catalog context.
    """
    def __init__(self, songs: List[Song]):
        if not songs:
            raise ValueError("Recommender requires at least one song.")
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top songs for compatibility with the starter tests."""
        return [result.song for result in self.recommend_with_context(user, k)]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        score, reasons = score_song(user.to_preferences(), song_to_dict(song))
        context = self.retrieve_context(user, song, k=2)
        confidence = confidence_from_score(score)
        context_titles = ", ".join(item.title for item in context) or "no close context songs"
        reason_text = "; ".join(reasons) if reasons else "limited direct preference match"
        return (
            f"{song.title} by {song.artist} scored {score:.2f} "
            f"with {confidence:.0%} confidence because {reason_text}. "
            f"Retrieved catalog evidence: {context_titles}."
        )

    def retrieve_context(self, user: UserProfile, candidate: Song, k: int = 3) -> List[Song]:
        """
        Retrieve songs that provide evidence for a recommendation.

        The candidate itself is excluded. The returned songs are close to both
        the user profile and the candidate's audio features, which makes the
        generated explanation grounded in the catalog instead of generic text.
        """
        if k < 1:
            return []

        user_prefs = user.to_preferences()
        candidate_dict = song_to_dict(candidate)
        context_scores = []
        for song in self.songs:
            if song.id == candidate.id:
                continue
            song_dict = song_to_dict(song)
            profile_score, _ = score_song(user_prefs, song_dict)
            similarity = song_similarity(candidate_dict, song_dict)
            context_scores.append((song, profile_score + similarity))

        ranked = sorted(context_scores, key=lambda item: item[1], reverse=True)
        return [song for song, _ in ranked[:k]]

    def recommend_with_context(self, user: UserProfile, k: int = 5) -> List[RecommendationResult]:
        """Rank songs and return RAG-grounded recommendation objects."""
        if k < 1:
            raise ValueError("k must be at least 1.")

        scored = []
        for song in self.songs:
            score, _ = score_song(user.to_preferences(), song_to_dict(song))
            scored.append((song, score))

        ranked = sorted(scored, key=lambda item: item[1], reverse=True)[:k]
        results = []
        for song, score in ranked:
            context = self.retrieve_context(user, song, k=3)
            explanation = self.explain_recommendation(user, song)
            results.append(
                RecommendationResult(
                    song=song,
                    score=score,
                    confidence=confidence_from_score(score),
                    retrieved_context=context,
                    explanation=explanation,
                )
            )

        logger.info(
            "Generated %s recommendations for genre=%s mood=%s target_energy=%.2f",
            len(results),
            user.favorite_genre,
            user.favorite_mood,
            user.target_energy,
        )
        return results

    def generate_playlist_summary(self, user: UserProfile, k: int = 3) -> str:
        """Generate a short answer using only retrieved recommendation evidence."""
        recommendations = self.recommend_with_context(user, k=k)
        if not recommendations:
            return "No grounded recommendations were available."

        lines = [
            (
                f"{index}. {result.song.title} by {result.song.artist} "
                f"({result.confidence:.0%} confidence): {result.explanation}"
            )
            for index, result in enumerate(recommendations, start=1)
        ]
        return "\n".join(lines)


def song_to_dict(song: Song) -> Dict:
    return {
        "id": song.id,
        "title": song.title,
        "artist": song.artist,
        "genre": song.genre,
        "mood": song.mood,
        "energy": song.energy,
        "tempo_bpm": song.tempo_bpm,
        "valence": song.valence,
        "danceability": song.danceability,
        "acousticness": song.acousticness,
    }


def dict_to_song(row: Dict) -> Song:
    return Song(
        id=int(row["id"]),
        title=row["title"],
        artist=row["artist"],
        genre=row["genre"],
        mood=row["mood"],
        energy=float(row["energy"]),
        tempo_bpm=float(row["tempo_bpm"]),
        valence=float(row["valence"]),
        danceability=float(row["danceability"]),
        acousticness=float(row["acousticness"]),
    )


def confidence_from_score(score: float) -> float:
    """Normalize a recommendation score into a readable confidence estimate."""
    return max(0.0, min(1.0, score / 7.7))


def song_similarity(first: Dict, second: Dict) -> float:
    """Estimate similarity between two catalog songs on a compact 0-3 scale."""
    similarity = 0.0
    if first["genre"].lower() == second["genre"].lower():
        similarity += 0.9
    if first["mood"].lower() == second["mood"].lower():
        similarity += 0.9

    similarity += max(0.0, 1.0 - abs(first["energy"] - second["energy"]) / 0.5) * 0.5
    similarity += max(0.0, 1.0 - abs(first["tempo_bpm"] - second["tempo_bpm"]) / 60.0) * 0.4
    similarity += max(0.0, 1.0 - abs(first["acousticness"] - second["acousticness"]) / 0.7) * 0.3
    return similarity

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs from a CSV file and return them as dictionaries."""
    path = Path(csv_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent.parent / path

    songs: List[Dict] = []
    if not path.exists():
        logger.error("Song catalog not found: %s", path)
        raise FileNotFoundError(f"Song catalog not found: {path}")

    with path.open(newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        required_columns = {
            "id", "title", "artist", "genre", "mood", "energy",
            "tempo_bpm", "valence", "danceability", "acousticness",
        }
        missing_columns = required_columns.difference(reader.fieldnames or [])
        if missing_columns:
            raise ValueError(f"Missing required song columns: {sorted(missing_columns)}")

        for row in reader:
            try:
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
            except (TypeError, ValueError) as exc:
                logger.warning("Skipping invalid song row %s: %s", row, exc)

    logger.info("Loaded %s songs from %s", len(songs), path)
    return songs


def load_song_objects(csv_path: str) -> List[Song]:
    """Load songs from CSV as Song dataclass instances."""
    return [dict_to_song(row) for row in load_songs(csv_path)]


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
    target_energy = clamp(float(get_pref("target_energy", "energy", default=0.5)), 0.0, 1.0)
    target_tempo = float(get_pref("target_tempo_bpm", "tempo_bpm", default=100.0))
    target_valence = clamp(float(get_pref("target_valence", "valence", default=0.5)), 0.0, 1.0)
    target_danceability = clamp(float(get_pref("target_danceability", "danceability", default=0.5)), 0.0, 1.0)
    target_acousticness = clamp(float(get_pref("target_acousticness", "acousticness", default=0.5)), 0.0, 1.0)

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


def clamp(value: float, minimum: float, maximum: float) -> float:
    if value < minimum:
        logger.warning("Clamped preference value %.2f to %.2f", value, minimum)
        return minimum
    if value > maximum:
        logger.warning("Clamped preference value %.2f to %.2f", value, maximum)
        return maximum
    return value

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
