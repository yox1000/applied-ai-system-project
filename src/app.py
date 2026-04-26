import logging

import streamlit as st

try:
    from .evaluator import evaluate_recommender, summarize_evaluation
    from .recommender import Recommender, UserProfile, load_song_objects
except ImportError:
    from evaluator import evaluate_recommender, summarize_evaluation
    from recommender import Recommender, UserProfile, load_song_objects


logging.basicConfig(
    filename="recommender.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@st.cache_resource
def build_recommender() -> Recommender:
    songs = load_song_objects("data/songs.csv")
    return Recommender(songs)


def render_result(result, index: int) -> None:
    song = result.song
    with st.container(border=True):
        st.subheader(f"{index}. {song.title}")
        st.caption(f"{song.artist} | {song.genre} | {song.mood}")

        score_col, confidence_col, energy_col = st.columns(3)
        score_col.metric("Score", f"{result.score:.2f}")
        confidence_col.metric("Confidence", f"{result.confidence:.0%}")
        energy_col.metric("Energy", f"{song.energy:.2f}")

        st.markdown("**Retrieved evidence**")
        evidence = ", ".join(context_song.title for context_song in result.retrieved_context)
        st.write(evidence or "No retrieved evidence available.")

        st.markdown("**AI explanation**")
        st.write(result.explanation)


def main() -> None:
    st.set_page_config(
        page_title="Music Recommender RAG System",
        page_icon="🎧",
        layout="wide",
    )

    recommender = build_recommender()

    st.title("Music Recommender RAG System")
    st.write(
        "Choose a listener profile. The app scores songs, retrieves related catalog "
        "evidence, and explains each recommendation using that evidence."
    )

    with st.sidebar:
        st.header("Listener Profile")
        preset = st.selectbox(
            "Preset",
            ["High-Energy Pop", "Chill Lofi", "Deep Intense Rock", "Custom"],
        )

        presets = {
            "High-Energy Pop": ("pop", "happy", 0.90, False),
            "Chill Lofi": ("lofi", "chill", 0.25, True),
            "Deep Intense Rock": ("rock", "intense", 0.85, False),
            "Custom": ("pop", "happy", 0.50, False),
        }
        default_genre, default_mood, default_energy, default_acoustic = presets[preset]

        genres = sorted({song.genre for song in recommender.songs})
        moods = sorted({song.mood for song in recommender.songs})

        genre = st.selectbox("Favorite genre", genres, index=genres.index(default_genre))
        mood = st.selectbox("Favorite mood", moods, index=moods.index(default_mood))
        target_energy = st.slider("Target energy", 0.0, 1.0, default_energy, 0.05)
        likes_acoustic = st.toggle("Prefer acoustic songs", value=default_acoustic)
        count = st.slider("Number of recommendations", 1, 5, 3)

    profile = UserProfile(
        favorite_genre=genre,
        favorite_mood=mood,
        target_energy=target_energy,
        likes_acoustic=likes_acoustic,
    )

    st.header("Recommendations")
    recommendations = recommender.recommend_with_context(profile, k=count)
    for index, result in enumerate(recommendations, start=1):
        render_result(result, index)

    st.header("Reliability Evaluation")
    evaluation_results = evaluate_recommender(recommender)
    passed = sum(1 for result in evaluation_results if result.passed)
    st.metric("Evaluation cases passed", f"{passed}/{len(evaluation_results)}")
    st.write(summarize_evaluation(evaluation_results))

    for result in evaluation_results:
        status = "PASS" if result.passed else "FAIL"
        with st.expander(f"{status}: {result.name} -> {result.top_song}"):
            st.write(f"Confidence: {result.confidence:.0%}")
            st.json(result.checks)


if __name__ == "__main__":
    main()
