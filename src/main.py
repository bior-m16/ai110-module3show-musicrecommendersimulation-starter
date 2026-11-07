"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, max_score, recommend_songs

WIDTH = 64
LOW_CONFIDENCE = 0.60   # warn when the best score is below this share of the maximum


def format_recommendations(user_prefs: dict, recommendations: list) -> str:
    """Build a readable block of text: profile header, then ranked songs with reasons."""
    top = max_score(user_prefs)
    prefs = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    lines = [
        "=" * WIDTH,
        "TOP RECOMMENDATIONS",
        f"Profile: {prefs}",
        "=" * WIDTH,
    ]
    if recommendations and recommendations[0][1] < LOW_CONFIDENCE * top:
        lines.append("WARNING: no song fits this profile well (best score is under 60% of the maximum).")
        lines.append("-" * WIDTH)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        lines.append(f"{rank}. {song['title']} - {song['artist']}")
        lines.append(f"   Score: {score:.2f} / {top:.2f}   ({song['genre']}, {song['mood']})")
        for reason in explanation.split("; "):
            lines.append(f"     - {reason}")
        lines.append("-" * WIDTH)
    return "\n".join(lines)


# Standard profiles: clear, consistent tastes the system should handle well.
STANDARD_PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.85, "acousticness": 0.15},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.38, "acousticness": 0.80},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.92, "acousticness": 0.10},
}

# Adversarial profiles: edge cases designed to expose weaknesses in the scoring logic.
ADVERSARIAL_PROFILES = {
    "Conflicting: sad but high-energy": {"genre": "blues", "mood": "sad", "energy": 0.90},
    "Conflicting: high-energy but fully acoustic": {"genre": "ambient", "mood": "peaceful", "energy": 0.95, "acousticness": 0.95},
    "Genre and mood not in catalog": {"genre": "k-pop", "mood": "bubbly", "energy": 0.80},
    "Dead-center energy only": {"energy": 0.50},
}


def run_profile(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print the top k recommendations for one named profile."""
    print(f"\n##### {name} #####")
    recommendations = recommend_songs(user_prefs, songs, k=k)
    print(format_recommendations(user_prefs, recommendations))


def main() -> None:
    """Load the catalog and print the top 5 for every standard and adversarial profile."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for name, prefs in {**STANDARD_PROFILES, **ADVERSARIAL_PROFILES}.items():
        run_profile(name, prefs, songs)


if __name__ == "__main__":
    main()
