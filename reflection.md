# Reflection

## Profile Comparisons

- **High-Energy Pop vs Chill Lofi:** The High-Energy Pop profile produces recommendations that favor bright, fast songs with exact `pop` genre and high energy. In contrast, the Chill Lofi profile shifts to slower, softer `lofi` tracks even when the exact mood label `calm` is not available, because genre and low energy still dominate. This makes sense because the model now weights energy more heavily than genre, so the low-energy preference strongly steers the output toward mellow songs.

- **High-Energy Pop vs Deep Intense Rock:** Both profiles prefer energetic music, but the High-Energy Pop profile prioritizes songs with `pop` and `happy` attributes, while Deep Intense Rock prioritizes exact `rock` genre and `intense` mood. The difference shows how changing genre and mood changes the top recommendations even when energy is similar, which aligns with the scoring logic: genre and mood both add fixed bonus points on top of the energy score.

- **Chill Lofi vs Deep Intense Rock:** These two profiles produce almost opposite outputs because one is looking for low-energy, relaxed music and the other is looking for high-energy, aggressive music. The Deep Intense Rock profile is likely to surface a precise `rock`/`intense` match like "Storm Runner," while the Chill Lofi profile will favor `lofi` songs with lower energy. That distinguishes the two profiles clearly and matches the expected behavior of the recommender.
