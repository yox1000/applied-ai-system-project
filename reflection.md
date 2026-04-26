# Reflection

## What I Built

I built on the original music recommender simulation by turning it into a catalog-grounded AI recommendation system. The original project scored songs from a CSV file. This version still scores songs, but it also retrieves similar catalog evidence, generates explanations, estimates confidence, logs runtime behavior, and runs reliability checks.

## Limitations and Biases

The biggest limitation is the small dataset. With only 18 songs, the system cannot represent all genres, artists, cultures, or listening situations. The recommender is also biased toward exact metadata labels, so a song can be unfairly ranked lower if its genre or mood label does not exactly match the user's profile.

Another limitation is that confidence is based on a scoring formula, not real-world user satisfaction. A high confidence score means the song matches the available metadata well, not that a real listener will definitely enjoy it.

## Possible Misuse and Prevention

This system could be misused if someone treated it as a complete personalization tool or used it to make claims about a user's identity or taste. To reduce this risk, I designed it to show explanations, retrieved evidence, and confidence scores. The app also keeps logs and uses tests so recommendation behavior can be checked instead of accepted blindly.

## Reliability Testing Surprise

The most surprising part was how easily a small weight or label choice changed the output. A song with the right energy could lose to a song with a better exact mood match. This made me realize that AI reliability is not only about whether the code runs; it is also about whether the system's assumptions match the real task.

## Collaboration With AI

AI was helpful when suggesting that RAG would fit this project. Since the recommender already had a song catalog, retrieving relevant songs before generating an explanation made the project stronger and more explainable.

AI was flawed when it initially treated the starter recommender as if the object-oriented `recommend()` method already worked. After reading the code, I found that it returned the first `k` songs without scoring. I fixed that by implementing actual ranking, retrieved context, confidence scoring, and tests.

## What I Learned

This project taught me that an AI system needs more than a useful output. It needs clear data flow, evaluation, error handling, and documentation. Building the RAG workflow helped me understand how retrieval can make AI output more grounded and easier to inspect.

I also learned that responsible AI design means being honest about limitations. The recommender is useful as a learning project, but it should not be presented as a complete music intelligence system.
