import pytest

from src.evaluator import evaluate_recommender, summarize_evaluation
from src.recommender import Song, UserProfile, Recommender, confidence_from_score, score_song

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""
    assert "Retrieved catalog evidence" in explanation


def test_recommend_with_context_returns_grounded_results():
    user = UserProfile(
        favorite_genre="lofi",
        favorite_mood="chill",
        target_energy=0.4,
        likes_acoustic=True,
    )
    rec = make_small_recommender()
    results = rec.recommend_with_context(user, k=1)

    assert len(results) == 1
    assert results[0].song.title == "Chill Lofi Loop"
    assert 0 <= results[0].confidence <= 1
    assert results[0].retrieved_context
    assert "Chill Lofi Loop" in results[0].explanation


def test_invalid_k_raises_value_error():
    rec = make_small_recommender()
    user = UserProfile("pop", "happy", 0.8, likes_acoustic=False)

    with pytest.raises(ValueError):
        rec.recommend_with_context(user, k=0)


def test_confidence_score_is_clamped():
    assert confidence_from_score(-1) == 0.0
    assert confidence_from_score(100) == 1.0


def test_score_song_clamps_out_of_range_preferences():
    song = {
        "id": 1,
        "title": "Test",
        "artist": "Artist",
        "genre": "pop",
        "mood": "happy",
        "energy": 1.0,
        "tempo_bpm": 120,
        "valence": 0.9,
        "danceability": 0.8,
        "acousticness": 0.2,
    }
    score, reasons = score_song({"genre": "pop", "mood": "happy", "energy": 2.0}, song)

    assert score > 0
    assert reasons


def test_evaluator_reports_passed_cases():
    rec = make_small_recommender()
    results = evaluate_recommender(rec)
    summary = summarize_evaluation(results)

    assert len(results) == 3
    assert "out of" in summary
