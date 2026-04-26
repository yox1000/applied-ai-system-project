# Model Card: Music Recommender RAG System

## Model Name

**CatalogGrounded MelodyRanker**

## Intended Use

This system recommends songs from a small classroom catalog based on a user's preferred genre, mood, target energy, and acoustic preference. It is intended for learning, portfolio demonstration, and analysis of how recommenders can be made more explainable.

It is not intended for production music streaming, real user profiling, or high-stakes personalization.

## How It Works

The model uses a content-based scoring system. It awards points for exact genre and mood matches, then adds points when numeric audio features are close to the user's target preferences.

The advanced feature is a RAG-style retrieval workflow. For every recommended song, the system retrieves similar catalog songs as supporting evidence and uses that evidence in the final explanation. This makes the output more transparent than a plain ranked list.

## Data

The dataset is `data/songs.csv`, which contains 18 songs. Each song includes title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness.

The catalog includes pop, lofi, rock, ambient, jazz, synthwave, indie pop, classical, folk, hip hop, world, metal, R&B, reggaeton, and country. The dataset is small and hand-curated, so it cannot represent the full diversity of music or listener taste.

## Strengths

- Easy to inspect because every recommendation has scores and reasons.
- Grounded explanations use retrieved catalog evidence.
- Built-in confidence scores help users interpret recommendation strength.
- Automated tests and an evaluator check common success cases.

## Limitations and Bias

The system can overvalue exact labels like `genre` and `mood`. If a user's taste is flexible or if a song is mislabeled, the ranking may be too narrow. The small dataset can also create genre imbalance, because some styles have more nearby support songs than others.

The confidence score is not a true probability. It is a normalized version of the scoring rule, so it should be read as a rough strength signal.

## Evaluation

The app evaluates three representative profiles:

- high-energy pop
- chill lofi
- intense rock

Current result:

```text
3 out of 3 evaluation cases passed; average top-result confidence was 66%.
```

The automated tests check ranking behavior, grounded explanations, context retrieval, confidence clamping, invalid input handling, and evaluator output.

## Ethical Considerations

The system could be misused if someone presented it as a complete model of a person's musical identity. It only knows a tiny catalog and a few user preferences. To reduce that risk, the app exposes explanations, logs runtime behavior, and keeps recommendations auditable.

The system also risks reinforcing narrow taste categories. A real recommender should include diversity controls, user feedback, and careful review of whether some genres or artists are systematically underrepresented.

## Future Work

- Add feedback so users can reject or approve recommendations.
- Add diversity rules so the list does not become too repetitive.
- Expand the catalog and include richer metadata.
- Replace template explanations with an LLM, while still grounding the answer in retrieved catalog rows.
- Add human evaluation forms for peer review.

## Personal Reflection

The most important lesson was that explainability changes how useful an AI system feels. A ranked list is helpful, but a ranked list with retrieved evidence, confidence, and tests is easier to trust and easier to debug.

AI assistance helped identify RAG as a good fit for a catalog recommender. One AI suggestion that needed correction was assuming the starter `Recommender` class already ranked songs. Manual code review showed that method was still a placeholder, so I implemented the actual ranking and added tests to verify it.
