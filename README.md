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

**Energy tolerance rule:** if a song's energy is more than 0.30 away from the user's target, its mood and genre bonuses are halved (and the reason says so). Without it, a label match could outvote a clear energy request.

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

Output for the default pop/happy profile from an earlier single-profile run (`main.py` now runs seven profiles, shown under "Experiments You Tried"):

```text
Loading songs from data/songs.csv...
Loaded songs: 20

================================================================
TOP RECOMMENDATIONS
Profile: genre=pop, mood=happy, energy=0.8, acousticness=0.2
================================================================
1. Sunrise City - Neon Echo
   Score: 6.92 / 7.00   (pop, happy)
     - mood match: happy (+2.00)
     - genre match: pop (+1.00)
     - energy 0.82 vs target 0.80 (+2.94)
     - acousticness 0.18 vs target 0.20 (+0.98)
----------------------------------------------------------------
2. Rooftop Lights - Indigo Parade
   Score: 5.73 / 7.00   (indie pop, happy)
     - mood match: happy (+2.00)
     - energy 0.76 vs target 0.80 (+2.88)
     - acousticness 0.35 vs target 0.20 (+0.85)
----------------------------------------------------------------
3. Gym Hero - Max Pulse
   Score: 4.46 / 7.00   (pop, intense)
     - genre match: pop (+1.00)
     - energy 0.93 vs target 0.80 (+2.61)
     - acousticness 0.05 vs target 0.20 (+0.85)
----------------------------------------------------------------
4. Concrete Crown - Dre Valen
   Score: 3.86 / 7.00   (hip hop, confident)
     - energy 0.78 vs target 0.80 (+2.94)
     - acousticness 0.12 vs target 0.20 (+0.92)
----------------------------------------------------------------
5. Night Drive Loop - Neon Echo
   Score: 3.83 / 7.00   (synthwave, moody)
     - energy 0.75 vs target 0.80 (+2.85)
     - acousticness 0.22 vs target 0.20 (+0.98)
----------------------------------------------------------------
```

Sunrise City ranks first because it matches on mood, genre, energy and acousticness. Rooftop Lights follows on mood and energy alone. Gym Hero ranks third on genre and energy despite its "intense" mood, which is one of the biases noted above.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Run everything with `python -m src.main`. The profiles live in `STANDARD_PROFILES` and `ADVERSARIAL_PROFILES` in [src/main.py](src/main.py). Each block below is the real terminal output. The score denominator is the most points that profile could earn (it only counts the preferences the profile sets).

### Standard profiles

#### High-Energy Pop

```text
================================================================
TOP RECOMMENDATIONS
Profile: genre=pop, mood=happy, energy=0.85, acousticness=0.15
================================================================
1. Sunrise City - Neon Echo
   Score: 6.88 / 7.00   (pop, happy)
     - mood match: happy (+2.00)
     - genre match: pop (+1.00)
     - energy 0.82 vs target 0.85 (+2.91)
     - acousticness 0.18 vs target 0.15 (+0.97)
----------------------------------------------------------------
2. Rooftop Lights - Indigo Parade
   Score: 5.53 / 7.00   (indie pop, happy)
     - mood match: happy (+2.00)
     - energy 0.76 vs target 0.85 (+2.73)
     - acousticness 0.35 vs target 0.15 (+0.80)
----------------------------------------------------------------
3. Gym Hero - Max Pulse
   Score: 4.66 / 7.00   (pop, intense)
     - genre match: pop (+1.00)
     - energy 0.93 vs target 0.85 (+2.76)
     - acousticness 0.05 vs target 0.15 (+0.90)
----------------------------------------------------------------
4. Fuego en la Calle - Los Cometas
   Score: 3.92 / 7.00   (latin, energetic)
     - energy 0.86 vs target 0.85 (+2.97)
     - acousticness 0.20 vs target 0.15 (+0.95)
----------------------------------------------------------------
5. Storm Runner - Voltline
   Score: 3.77 / 7.00   (rock, intense)
     - energy 0.91 vs target 0.85 (+2.82)
     - acousticness 0.10 vs target 0.15 (+0.95)
----------------------------------------------------------------
```

#### Chill Lofi

```text
================================================================
TOP RECOMMENDATIONS
Profile: genre=lofi, mood=chill, energy=0.38, acousticness=0.8
================================================================
1. Library Rain - Paper Lanterns
   Score: 6.85 / 7.00   (lofi, chill)
     - mood match: chill (+2.00)
     - genre match: lofi (+1.00)
     - energy 0.35 vs target 0.38 (+2.91)
     - acousticness 0.86 vs target 0.80 (+0.94)
----------------------------------------------------------------
2. Midnight Coding - LoRoom
   Score: 6.79 / 7.00   (lofi, chill)
     - mood match: chill (+2.00)
     - genre match: lofi (+1.00)
     - energy 0.42 vs target 0.38 (+2.88)
     - acousticness 0.71 vs target 0.80 (+0.91)
----------------------------------------------------------------
3. Spacewalk Thoughts - Orbit Bloom
   Score: 5.58 / 7.00   (ambient, chill)
     - mood match: chill (+2.00)
     - energy 0.28 vs target 0.38 (+2.70)
     - acousticness 0.92 vs target 0.80 (+0.88)
----------------------------------------------------------------
4. Focus Flow - LoRoom
   Score: 4.92 / 7.00   (lofi, focused)
     - genre match: lofi (+1.00)
     - energy 0.40 vs target 0.38 (+2.94)
     - acousticness 0.78 vs target 0.80 (+0.98)
----------------------------------------------------------------
5. Blue Hour Blues - Delta Mae
   Score: 3.93 / 7.00   (blues, sad)
     - energy 0.40 vs target 0.38 (+2.94)
     - acousticness 0.81 vs target 0.80 (+0.99)
----------------------------------------------------------------
```

#### Deep Intense Rock

```text
================================================================
TOP RECOMMENDATIONS
Profile: genre=rock, mood=intense, energy=0.92, acousticness=0.1
================================================================
1. Storm Runner - Voltline
   Score: 6.97 / 7.00   (rock, intense)
     - mood match: intense (+2.00)
     - genre match: rock (+1.00)
     - energy 0.91 vs target 0.92 (+2.97)
     - acousticness 0.10 vs target 0.10 (+1.00)
----------------------------------------------------------------
2. Gym Hero - Max Pulse
   Score: 5.92 / 7.00   (pop, intense)
     - mood match: intense (+2.00)
     - energy 0.93 vs target 0.92 (+2.97)
     - acousticness 0.05 vs target 0.10 (+0.95)
----------------------------------------------------------------
3. Pulse Overdrive - Kinetic Bloom
   Score: 3.81 / 7.00   (edm, euphoric)
     - energy 0.96 vs target 0.92 (+2.88)
     - acousticness 0.03 vs target 0.10 (+0.93)
----------------------------------------------------------------
4. Iron Requiem - Black Anvil
   Score: 3.81 / 7.00   (metal, angry)
     - energy 0.97 vs target 0.92 (+2.85)
     - acousticness 0.06 vs target 0.10 (+0.96)
----------------------------------------------------------------
5. Fuego en la Calle - Los Cometas
   Score: 3.72 / 7.00   (latin, energetic)
     - energy 0.86 vs target 0.92 (+2.82)
     - acousticness 0.20 vs target 0.10 (+0.90)
----------------------------------------------------------------
```

### Adversarial profiles (edge cases)

#### Conflicting: sad but high-energy

```text
================================================================
TOP RECOMMENDATIONS
Profile: genre=blues, mood=sad, energy=0.9
================================================================
WARNING: no song fits this profile well (best score is under 60% of the maximum).
----------------------------------------------------------------
1. Blue Hour Blues - Delta Mae
   Score: 3.00 / 6.00   (blues, sad)
     - mood match: sad (+1.00) [reduced: energy far from target]
     - genre match: blues (+0.50) [reduced: energy far from target]
     - energy 0.40 vs target 0.90 (+1.50)
----------------------------------------------------------------
2. Storm Runner - Voltline
   Score: 2.97 / 6.00   (rock, intense)
     - energy 0.91 vs target 0.90 (+2.97)
----------------------------------------------------------------
3. Gym Hero - Max Pulse
   Score: 2.91 / 6.00   (pop, intense)
     - energy 0.93 vs target 0.90 (+2.91)
----------------------------------------------------------------
4. Fuego en la Calle - Los Cometas
   Score: 2.88 / 6.00   (latin, energetic)
     - energy 0.86 vs target 0.90 (+2.88)
----------------------------------------------------------------
5. Pulse Overdrive - Kinetic Bloom
   Score: 2.82 / 6.00   (edm, euphoric)
     - energy 0.96 vs target 0.90 (+2.82)
----------------------------------------------------------------
```

#### Conflicting: high-energy but fully acoustic

```text
================================================================
TOP RECOMMENDATIONS
Profile: genre=ambient, mood=peaceful, energy=0.95, acousticness=0.95
================================================================
WARNING: no song fits this profile well (best score is under 60% of the maximum).
----------------------------------------------------------------
1. Pulse Overdrive - Kinetic Bloom
   Score: 3.05 / 7.00   (edm, euphoric)
     - energy 0.96 vs target 0.95 (+2.97)
     - acousticness 0.03 vs target 0.95 (+0.08)
----------------------------------------------------------------
2. Iron Requiem - Black Anvil
   Score: 3.05 / 7.00   (metal, angry)
     - energy 0.97 vs target 0.95 (+2.94)
     - acousticness 0.06 vs target 0.95 (+0.11)
----------------------------------------------------------------
3. Gym Hero - Max Pulse
   Score: 3.04 / 7.00   (pop, intense)
     - energy 0.93 vs target 0.95 (+2.94)
     - acousticness 0.05 vs target 0.95 (+0.10)
----------------------------------------------------------------
4. Storm Runner - Voltline
   Score: 3.03 / 7.00   (rock, intense)
     - energy 0.91 vs target 0.95 (+2.88)
     - acousticness 0.10 vs target 0.95 (+0.15)
----------------------------------------------------------------
5. Fuego en la Calle - Los Cometas
   Score: 2.98 / 7.00   (latin, energetic)
     - energy 0.86 vs target 0.95 (+2.73)
     - acousticness 0.20 vs target 0.95 (+0.25)
----------------------------------------------------------------
```

#### Genre and mood not in catalog

```text
================================================================
TOP RECOMMENDATIONS
Profile: genre=k-pop, mood=bubbly, energy=0.8
================================================================
WARNING: no song fits this profile well (best score is under 60% of the maximum).
----------------------------------------------------------------
1. Sunrise City - Neon Echo
   Score: 2.94 / 6.00   (pop, happy)
     - energy 0.82 vs target 0.80 (+2.94)
----------------------------------------------------------------
2. Concrete Crown - Dre Valen
   Score: 2.94 / 6.00   (hip hop, confident)
     - energy 0.78 vs target 0.80 (+2.94)
----------------------------------------------------------------
3. Rooftop Lights - Indigo Parade
   Score: 2.88 / 6.00   (indie pop, happy)
     - energy 0.76 vs target 0.80 (+2.88)
----------------------------------------------------------------
4. Night Drive Loop - Neon Echo
   Score: 2.85 / 6.00   (synthwave, moody)
     - energy 0.75 vs target 0.80 (+2.85)
----------------------------------------------------------------
5. Fuego en la Calle - Los Cometas
   Score: 2.82 / 6.00   (latin, energetic)
     - energy 0.86 vs target 0.80 (+2.82)
----------------------------------------------------------------
```

#### Dead-center energy only

```text
================================================================
TOP RECOMMENDATIONS
Profile: energy=0.5
================================================================
1. Dusty Back Road - Hank Willow
   Score: 2.94 / 3.00   (country, nostalgic)
     - energy 0.52 vs target 0.50 (+2.94)
----------------------------------------------------------------
2. Velvet Hours - Simone Ray
   Score: 2.94 / 3.00   (r&b, romantic)
     - energy 0.48 vs target 0.50 (+2.94)
----------------------------------------------------------------
3. Island Drift - Sun Rhythm
   Score: 2.85 / 3.00   (reggae, laid-back)
     - energy 0.55 vs target 0.50 (+2.85)
----------------------------------------------------------------
4. Midnight Coding - LoRoom
   Score: 2.76 / 3.00   (lofi, chill)
     - energy 0.42 vs target 0.50 (+2.76)
----------------------------------------------------------------
5. Focus Flow - LoRoom
   Score: 2.70 / 3.00   (lofi, focused)
     - energy 0.40 vs target 0.50 (+2.70)
----------------------------------------------------------------
```

### Weight-sensitivity experiment

I changed the weights in `src/recommender.py` and re-ran three profiles (top 3 shown).

| Weights | High-Energy Pop | Deep Intense Rock | Sad but high-energy |
|---|---|---|---|
| Baseline (energy 3, mood 2, genre 1) | Sunrise City, Rooftop Lights, Gym Hero | Storm Runner, Gym Hero, Pulse Overdrive | Blue Hour Blues, Storm Runner, Gym Hero |
| Genre weight 0 | Sunrise City, Rooftop Lights, **Fuego en la Calle** | Storm Runner, Gym Hero, Pulse Overdrive | Blue Hour Blues, Storm Runner, Gym Hero |
| Genre weight 3 | Sunrise City, **Gym Hero**, Rooftop Lights | Storm Runner, Gym Hero, Pulse Overdrive | Blue Hour Blues, Storm Runner, Gym Hero |
| Energy weight 1.5 (halved) | Sunrise City, Rooftop Lights, Gym Hero | Storm Runner, Gym Hero, **Iron Requiem** | Blue Hour Blues, Storm Runner, Gym Hero |

Takeaways: the #1 song never changed, so the winners are stable. Genre only reshuffles the middle of the list (at weight 3 Gym Hero overtakes Rooftop Lights, a pop-labelled workout track beating a happy indie song). Halving energy lets Iron Requiem (metal) into the rock fan's top 3, which is closer to what a rock fan would expect.

### Weight-shift experiment: double energy, halve genre

Change tested: energy weight 3.0 to 6.0, genre weight 1.0 to 0.5. Math check: the maximum score for a full profile becomes 6.0 + 2.0 + 0.5 + 1.0 = 9.5, `max_score` recalculates it from the constants, and no song scored above its maximum (highest 9.44 / 9.5).

Result: 6 of 7 profiles gave an identical top 5 in the same order. Only "sad but high-energy" changed: Storm Runner (energy 0.91) replaced Blue Hour Blues (energy 0.40) at #1. That is different rather than more accurate, since it honors the energy request and drops the sad mood. The ranking is stable under this change.

### Fix attempt: label matches overriding energy

Problem: for "sad but high-energy" (energy 0.90), a slow blues song (energy 0.40) won because mood and genre matches added 3.00 points, more than the 1.5 it lost on energy.

Two changes, both in the code:
1. **Energy tolerance rule** (`ENERGY_TOLERANCE = 0.30`, `FAR_LABEL_SCALE = 0.5` in `src/recommender.py`): when a song's energy is more than 0.30 from the target, its mood and genre bonuses are halved.
2. **Low-confidence warning** (`LOW_CONFIDENCE = 0.60` in `src/main.py`): if the best score is under 60% of the profile's maximum, the output starts with a warning.

Results (before and after, top match shown):

| Profile | Before | After |
|---|---|---|
| Sad but high-energy | Blue Hour Blues, 4.50 / 6.00 | Blue Hour Blues, 3.00 / 6.00, **plus warning**. Storm Runner is now 2.97, a near tie |
| High-energy but fully acoustic | Moonlit Sonata Remix (energy 0.18), 3.67 | Pulse Overdrive (energy 0.96), **plus warning** |
| Genre and mood not in catalog | Sunrise City, 2.94 | Same ranking, **plus warning** |
| High-Energy Pop, Chill Lofi, Deep Intense Rock, Dead-center energy | unchanged | unchanged, no warning |

What this shows: the fix did what it was meant to on the acoustic conflict (a quiet classical piece no longer wins a request for energy 0.95), and the standard profiles are untouched. On "sad but high-energy" it did not change the winner. The blues song still edges out Storm Runner by 0.03, but the score is now honest about how weak the match is, and the warning tells the user. That may be the right outcome: no song in the catalog is both sad and high-energy, so the system should say so instead of pretending.

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



