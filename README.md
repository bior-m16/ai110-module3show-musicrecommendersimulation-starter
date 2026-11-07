# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world platforms like Spotify and YouTube combine two ideas. **Collaborative filtering** learns from the behavior of millions of users (plays, skips, likes, playlist co-occurrence) to find people with similar taste. **Content-based filtering** compares the attributes of songs (genre, tempo, energy, mood, audio embeddings) to what a user already likes. At scale, they blend both: a fast stage narrows millions of tracks to a few hundred candidates, then a ranking model scores those using richer signals such as skips, time of day and listening history. My simulation is a small **content-based** recommender. It has no multi-user behavior data, so it compares each song's attributes to a single user's stated preferences and prioritizes how well a song matches the user's **mood** and **energy level**, with genre as a smaller bonus.

### Features

**`Song`** (from `data/songs.csv`): `id`, `title`, `artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`.

**`UserProfile`**: `favorite_genre`, `favorite_mood`, `target_energy`, `likes_acoustic`.

Only `genre`, `mood`, `energy` and `acousticness` are used for scoring. Valence and danceability overlap heavily with energy, and tempo would need normalizing, so they are left out of this version.

### Data Flow

```
INPUT                      PROCESS (the loop)                          OUTPUT
-----                      ------------------                          ------
User profile      +        data/songs.csv (20 songs)
{genre, mood,                    |
 energy,                         v
 acousticness}           load_songs()  -> list of song dicts
      |                          |
      |                          v
      |                  for each song:
      +--------------->    score_song(user, song)
                               |  + 3.0 * energy closeness
                               |  + 2.0 * mood match
                               |  + 1.0 * genre match
                               |  + 1.0 * acousticness closeness
                               v
                         (song, score, reasons)
                                 |
                                 v
                         sort by score, high to low   <- Ranking Rule
                                 |
                                 v
                         take top K  ->  "Top recommendations" + explanation
```

One song's journey: a CSV row becomes a dict, `score_song` compares it with the user profile and returns a number plus the reasons for it, and the whole list of scored songs is sorted, so the K best end up at the top.

### Algorithm Recipe

**Scoring Rule** (one song vs. the user), maximum 7.0:

```
score = 3.0 * (1 - |song.energy - target_energy|)     # closeness, 0 to 3
      + 2.0 * mood_match                              # 1 if equal, else 0
      + 1.0 * genre_match                             # 1 if equal, else 0
      + 1.0 * (1 - |song.acousticness - target|)      # closeness, 0 to 1
```

Numeric features use a **closeness** score, `1 - |song_value - user_target|`, instead of "higher is better". A song exactly on target gets full points, and points fall off as it gets further away in either direction. A user who wants 0.4 energy is not served by a 0.9 song just because it has more energy. This works for features scaled 0 to 1. Tempo would first be scaled with `(bpm - 60) / (152 - 60)`.

**Weights:** energy (3.0) > mood (2.0) > genre (1.0) = acousticness (1.0). Mood outweighs genre because it describes the listening situation, and two songs in the same genre can feel completely different (Gym Hero vs. Sunrise City). Genre is a coarse label, and most genres in this catalog have only one song. Energy gets the most weight because it is continuous, so it ranks every song and breaks ties between songs that share a mood or genre.

**Ranking Rule** (the whole catalog): score every song, sort by score from highest to lowest, and return the top `k`.

Both rules are needed because they answer different questions. The Scoring Rule judges one song in isolation ("how well does this fit?") and produces a number. That number alone recommends nothing. The Ranking Rule compares all those numbers, orders them and cuts the list to the best `k`. A score can't pick a winner by itself, and a ranking is meaningless without a consistent score to sort by. Keeping them separate also lets you change one without touching the other, for example adjusting weights, or adding a rule that avoids repeating the same artist.

**Starter user profile:** `{"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.2}`. It will be tested against contrasting profiles (intense rock, chill lofi, a conflicting rock + chill profile, and a genre missing from the catalog) to check that the system can tell very different tastes apart.

### Expected Biases and Limitations

- **Energy dominates.** It carries 43% of the maximum score, so songs with the right energy can outrank songs that match the user's mood or genre. Example: Gym Hero (pop, intense) ranks third for a pop/happy user.
- **Exact-match categories.** "Happy" does not match "euphoric" or "energetic", and a related genre such as indie pop gets no genre credit for a pop fan. Great songs that are close but not identical get penalized.
- **Genre imbalance.** Lofi has 3 songs and most other genres have 1, so lofi fans get a fuller list of strong matches than fans of jazz, metal or country.
- **Small catalog.** With 20 songs, the lower half of any top-5 list will be weak matches.
- **Redundant features.** Energy, acousticness and danceability are correlated, so scoring several of them double-counts the same "intensity" signal.
- **One static profile.** There is no learning from skips or likes, so the system can't adapt, and it tends to keep returning similar songs (a filter bubble).
- **Conflicting tastes.** A profile like rock + chill returns a mediocre best match with no warning that nothing fits well.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



