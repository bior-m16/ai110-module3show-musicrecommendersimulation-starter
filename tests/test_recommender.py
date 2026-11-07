from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# --- Functional API: load_songs, score_song, recommend_songs ---

import pytest

from src.recommender import load_songs, recommend_songs, score_song


def make_song(**overrides) -> dict:
    song = {
        "id": 1,
        "title": "Test Song",
        "artist": "Test Artist",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "tempo_bpm": 120.0,
        "valence": 0.7,
        "danceability": 0.7,
        "acousticness": 0.2,
    }
    song.update(overrides)
    return song


def test_load_songs_converts_numeric_fields():
    songs = load_songs("data/songs.csv")
    assert len(songs) > 0
    first = songs[0]
    assert isinstance(first["id"], int)
    for field in ("energy", "tempo_bpm", "valence", "danceability", "acousticness"):
        assert isinstance(first[field], float)
    assert isinstance(first["genre"], str)


def test_score_song_perfect_match_gets_full_points():
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.2}
    score, reasons = score_song(prefs, make_song())
    assert score == pytest.approx(7.0)
    assert len(reasons) == 4


def test_score_song_mood_is_worth_more_than_genre():
    prefs = {"genre": "pop", "mood": "happy"}
    mood_only, _ = score_song(prefs, make_song(genre="rock"))
    genre_only, _ = score_song(prefs, make_song(mood="sad"))
    assert mood_only > genre_only


def test_score_song_rewards_closeness_not_higher_values():
    prefs = {"energy": 0.4}
    close, _ = score_song(prefs, make_song(energy=0.42))
    far_above, _ = score_song(prefs, make_song(energy=0.95))
    far_below, _ = score_song(prefs, make_song(energy=0.05))
    assert close > far_above
    assert close > far_below


def test_score_song_closeness_is_symmetric():
    prefs = {"energy": 0.5}
    above, _ = score_song(prefs, make_song(energy=0.7))
    below, _ = score_song(prefs, make_song(energy=0.3))
    assert above == pytest.approx(below)


def test_score_song_reasons_include_points():
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    _, reasons = score_song(prefs, make_song())
    assert any("mood match" in r and "+2.00" in r for r in reasons)
    assert any("genre match" in r and "+1.00" in r for r in reasons)
    assert any("energy" in r for r in reasons)


def test_score_song_no_match_gives_no_categorical_reasons():
    prefs = {"genre": "metal", "mood": "angry"}
    score, reasons = score_song(prefs, make_song())
    assert score == 0.0
    assert reasons == []


def test_score_song_skips_missing_preferences():
    # Only energy is given, so acousticness must not contribute.
    score, reasons = score_song({"energy": 0.8}, make_song())
    assert score == pytest.approx(3.0)
    assert len(reasons) == 1


def test_recommend_songs_sorted_highest_first_and_limited_to_k():
    songs = load_songs("data/songs.csv")
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    results = recommend_songs(prefs, songs, k=3)
    assert len(results) == 3
    scores = [score for _, score, _ in results]
    assert scores == sorted(scores, reverse=True)
    assert results[0][0]["title"] == "Sunrise City"


def test_recommend_songs_distinguishes_rock_from_lofi():
    songs = load_songs("data/songs.csv")
    rock = recommend_songs({"genre": "rock", "mood": "intense", "energy": 0.92}, songs, k=3)
    lofi = recommend_songs({"genre": "lofi", "mood": "chill", "energy": 0.38}, songs, k=3)
    assert rock[0][0]["genre"] == "rock"
    assert lofi[0][0]["genre"] == "lofi"
    rock_titles = {s["title"] for s, _, _ in rock}
    lofi_titles = {s["title"] for s, _, _ in lofi}
    assert rock_titles.isdisjoint(lofi_titles)


def test_recommend_songs_does_not_modify_input_list():
    songs = load_songs("data/songs.csv")
    original_order = [s["id"] for s in songs]
    recommend_songs({"genre": "pop", "mood": "happy", "energy": 0.8}, songs, k=5)
    assert [s["id"] for s in songs] == original_order


def test_recommend_songs_ties_keep_catalog_order():
    songs = [make_song(id=1, title="A"), make_song(id=2, title="B")]
    results = recommend_songs({"genre": "pop", "mood": "happy"}, songs, k=2)
    assert [s["title"] for s, _, _ in results] == ["A", "B"]


def test_recommend_songs_k_larger_than_catalog():
    songs = [make_song(id=1), make_song(id=2)]
    assert len(recommend_songs({"mood": "happy"}, songs, k=10)) == 2


def test_recommender_class_explanation_lists_matches():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.4,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    explanation = rec.explain_recommendation(user, rec.songs[0])
    assert "mood match" in explanation


def test_score_song_far_energy_reduces_label_bonuses():
    prefs = {"mood": "sad", "genre": "blues", "energy": 0.9}
    near, _ = score_song(prefs, make_song(mood="sad", genre="blues", energy=0.85))
    far, reasons = score_song(prefs, make_song(mood="sad", genre="blues", energy=0.40))
    # Near: 2.0 + 1.0 + 3*(1-0.05) = 5.85. Far: (2.0 + 1.0) * 0.5 + 3*(1-0.5) = 3.0
    assert near == pytest.approx(5.85)
    assert far == pytest.approx(3.0)
    assert any("reduced" in r for r in reasons)


def test_score_song_label_bonus_unchanged_within_tolerance():
    prefs = {"mood": "happy", "energy": 0.8}
    score, reasons = score_song(prefs, make_song(energy=0.6))  # gap 0.2 <= 0.30
    assert score == pytest.approx(2.0 + 3.0 * 0.8)
    assert not any("reduced" in r for r in reasons)


def test_conflicting_profile_is_now_a_close_race():
    songs = [
        make_song(id=1, title="Slow Sad", mood="sad", genre="blues", energy=0.40),
        make_song(id=2, title="Loud Neutral", mood="intense", genre="rock", energy=0.91),
    ]
    prefs = {"mood": "sad", "genre": "blues", "energy": 0.9}
    results = recommend_songs(prefs, songs, k=2)
    # Labels no longer win by a wide margin: the two songs are nearly tied.
    assert abs(results[0][1] - results[1][1]) < 0.1
