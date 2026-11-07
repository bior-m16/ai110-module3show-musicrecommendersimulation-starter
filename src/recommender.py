import csv
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Tuple

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

# Scoring weights (max score = 6.0 without the acoustic bonus, 7.0 with it)
MOOD_WEIGHT = 2.0
GENRE_WEIGHT = 1.0
ENERGY_WEIGHT = 3.0
ACOUSTIC_WEIGHT = 1.0


def _profile_to_prefs(user: UserProfile) -> Dict:
    """Convert a UserProfile into the dict format used by score_song."""
    prefs = {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
        "acousticness": 0.8 if user.likes_acoustic else 0.2,
    }
    return prefs


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        prefs = _profile_to_prefs(user)
        ranked = sorted(
            self.songs,
            key=lambda s: score_song(prefs, asdict(s))[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, reasons = score_song(_profile_to_prefs(user), asdict(song))
        return "; ".join(reasons) if reasons else "No strong matches"


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file, converting numeric columns to numbers.
    Required by src/main.py
    """
    print(f"Loading songs from {csv_path}...")
    int_fields = ("id",)
    float_fields = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for key in int_fields:
                row[key] = int(row[key])
            for key in float_fields:
                row[key] = float(row[key])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    Recipe (max 7.0):
      +2.0 mood match (exact)
      +1.0 genre match (exact)
      +3.0 * (1 - |song energy - target energy|)
      +1.0 * (1 - |song acousticness - target|)   (only if the user gave one)
    Returns (score, reasons), where each reason names the points it added.
    """
    score = 0.0
    reasons: List[str] = []

    if song["mood"] == user_prefs.get("mood"):
        score += MOOD_WEIGHT
        reasons.append(f"mood match: {song['mood']} (+{MOOD_WEIGHT:.2f})")

    if song["genre"] == user_prefs.get("genre"):
        score += GENRE_WEIGHT
        reasons.append(f"genre match: {song['genre']} (+{GENRE_WEIGHT:.2f})")

    # Numeric features: reward closeness to the target, not bigger or smaller.
    for feature, weight in (("energy", ENERGY_WEIGHT), ("acousticness", ACOUSTIC_WEIGHT)):
        if feature in user_prefs:
            diff = abs(song[feature] - user_prefs[feature])
            points = weight * (1 - diff)
            score += points
            reasons.append(
                f"{feature} {song[feature]:.2f} vs target {user_prefs[feature]:.2f} (+{points:.2f})"
            )

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Scores every song with score_song, then returns the top k as
    (song, score, explanation), highest score first.
    """
    scored = [
        (song, score, "; ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]
    return sorted(scored, key=lambda item: item[1], reverse=True)[:k]
