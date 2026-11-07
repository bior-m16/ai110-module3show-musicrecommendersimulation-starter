"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs

WIDTH = 64


def format_recommendations(user_prefs: dict, recommendations: list) -> str:
    """Build a readable block of text: profile header, then ranked songs with reasons."""
    prefs = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    lines = [
        "=" * WIDTH,
        "TOP RECOMMENDATIONS",
        f"Profile: {prefs}",
        "=" * WIDTH,
    ]
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        lines.append(f"{rank}. {song['title']} - {song['artist']}")
        lines.append(f"   Score: {score:.2f} / 7.00   ({song['genre']}, {song['mood']})")
        for reason in explanation.split("; "):
            lines.append(f"     - {reason}")
        lines.append("-" * WIDTH)
    return "\n".join(lines)


def main() -> None:
    """Load the catalog, score it for the default profile, and print the top 5."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.2}

    recommendations = recommend_songs(user_prefs, songs, k=5)
    print(format_recommendations(user_prefs, recommendations))


if __name__ == "__main__":
    main()
