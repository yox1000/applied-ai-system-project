# 🎧 Model Card: Music Recommender Simulation

## Model Name

**Energy-Genre MelodyRanker**

## Goal / Task

This recommender tries to suggest songs that best match a user’s favorite genre, mood, and target energy level. It is designed to predict which songs in a small catalog are most likely to feel right for someone who can express those preferences.

## Data Used

The model uses a dataset of 18 songs from `data/songs.csv`. Each song includes features such as genre, mood, energy, tempo, valence, danceability, and acousticness. The dataset covers a modest variety of styles including pop, lofi, rock, jazz, synthwave, classical, folk, hip hop, world, metal, R&B, reggaeton, and ambient. It is limited in size, lacks user ratings and listening history, and does not represent the full diversity of musical taste.

## Algorithm Summary

The model assigns each song a score based on how well it matches the user’s preferences. It gives bonus points when a song matches the requested genre and mood exactly, and it rewards songs whose energy level is close to the user’s target. Additional song characteristics like tempo, valence, danceability, and acousticness also contribute to the score based on closeness to target values or default values. The final ranking is the sum of those weighted contributions.

## Observed Behavior / Biases

The system tends to favor songs that match energy very closely, which can narrow the recommendation list. Because energy is weighted heavily and uses a hard tolerance window, songs that are somewhat different in energy can be ignored entirely. Exact genre matching can also cause the model to miss related styles, and the system may underrepresent users who have more flexible or diverse musical tastes.

## Evaluation Process

I tested the recommender with a few distinct user profiles and compared the top recommendations for each. Example profiles included a high-energy pop listener, a low-energy lofi listener, and a deep intense rock listener. I reviewed whether the ranked songs reflected the expected genre and energy preferences, and I inspected the explanation strings to confirm how score contributions were being applied.

## Intended Use and Non-Intended Use

This system is intended for classroom exploration and prototype evaluation of recommender scoring logic. It is useful for demonstrating how feature weights influence ranking in a small music catalog. It is not intended for production use, broad personalization, or real-world music streaming services because the dataset is small and the model does not use real user behavior, popularity, or large-scale genre relationships.

## Ideas for Improvement

- Soften energy scoring so songs outside the exact tolerance still get partial credit.
- Support broader genre similarity rather than exact string matching.
- Add user listening history, acoustic preference handling, and diversity controls.

## Personal Reflection

My biggest learning moment was seeing how a single weight change could reshape the entire recommendation list. When energy became more important than genre, the model began favoring overall feel and tempo even more strongly, which highlighted how sensitive recommenders are to small scoring decisions.

Using AI tools helped me more quickly identify where the scoring logic lived and how to phrase the bias analysis, but I still needed to double-check the actual code and the final text manually. I verified the model’s weight values, confirmed the exact genre and energy scoring rules, and ensured the model card matched the requested structure.

I was surprised that even this simple algorithm could still produce recommendations that felt reasonable. By combining exact genre/mood match with numeric similarity on energy and other audio features, the model can surface songs that seem to fit a user’s vibe without any machine learning.

If I extended this project, I would try adding a softer similarity function for energy, broader genre matching for related styles, and simple user feedback or history so the recommender can learn from what listeners actually prefer.
