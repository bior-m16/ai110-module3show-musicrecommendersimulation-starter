"""
Tests organized by project step, so each phase of the assignment has a check.

Phase 1: the song catalog (data/songs.csv)
Phase 2: user profiles and the scoring recipe
Phase 3: loading, scoring, ranking and the CLI output
Phase 4: stress-test profiles, the weight experiment and the tolerance fix
Phase 5: documentation (README and model card)
"""

import csv
import inspect
from pathlib import Path

import pytest

import src.recommender as recommender
from src import main as cli
from src.recommender import (
    Recommender,
    Song,
    UserProfile,
    load_songs,
    max_score,
    recommend_songs,
    score_song,
)

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "songs.csv"
EXPECTED_HEADERS = [
    "id", "title", "artist", "genre", "mood", "energy",
    "tempo_bpm", "valence", "danceability", "acousticness",
]
STARTER_GENRES = {"pop", "lofi", "rock", "ambient", "jazz", "synthwave", "indie pop"}
STARTER_MOODS = {"happy", "chill", "intense", "relaxed", "moody", "focused"}
ZERO_TO_ONE = ("energy", "valence", "danceability", "acousticness")


@pytest.fixture(scope="module")
def songs():
    return load_songs(str(CSV_PATH))


def top_titles(profile, songs, k=5):
    return [song["title"] for song, _, _ in recommend_songs(profile, songs, k=k)]


# ---------------------------------------------------------------------------
# Phase 1: the data
# ---------------------------------------------------------------------------

def test_csv_has_expected_headers():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        assert next(csv.reader(f)) == EXPECTED_HEADERS


def test_catalog_was_expanded_beyond_starter_ten(songs):
    assert len(songs) >= 15


def test_song_ids_are_unique(songs):
    ids = [s["id"] for s in songs]
    assert len(ids) == len(set(ids))


def test_every_row_has_no_empty_fields():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            assert all(value.strip() != "" for value in row.values()), row


def test_zero_to_one_features_stay_in_range(songs):
    for song in songs:
        for field in ZERO_TO_ONE:
            assert 0.0 <= song[field] <= 1.0, (song["title"], field)


def test_tempo_is_a_plausible_bpm(songs):
    assert all(40 <= s["tempo_bpm"] <= 220 for s in songs)


def test_new_songs_add_new_genres_and_moods(songs):
    genres = {s["genre"] for s in songs}
    moods = {s["mood"] for s in songs}
    assert len(genres - STARTER_GENRES) >= 5
    assert len(moods - STARTER_MOODS) >= 5


def test_catalog_covers_low_and_high_energy(songs):
    energies = [s["energy"] for s in songs]
    assert min(energies) < 0.3
    assert max(energies) > 0.9


# ---------------------------------------------------------------------------
# Phase 2: user profile and the scoring recipe
# ---------------------------------------------------------------------------

def test_user_profile_has_the_planned_fields():
    profile = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    assert profile.favorite_genre == "pop"
    assert profile.favorite_mood == "happy"
    assert profile.target_energy == 0.8
    assert profile.likes_acoustic is False


def test_song_dataclass_has_all_csv_fields():
    assert set(Song.__dataclass_fields__) == set(EXPECTED_HEADERS)


def test_recipe_weights_are_energy_then_mood_then_genre():
    assert recommender.ENERGY_WEIGHT > recommender.MOOD_WEIGHT > recommender.GENRE_WEIGHT


def test_recipe_weights_match_the_documented_values():
    assert recommender.ENERGY_WEIGHT == 3.0
    assert recommender.MOOD_WEIGHT == 2.0
    assert recommender.GENRE_WEIGHT == 1.0
    assert recommender.ACOUSTIC_WEIGHT == 1.0


def test_max_score_for_full_profile_is_seven():
    full = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.2}
    assert max_score(full) == pytest.approx(7.0)


def test_max_score_counts_only_preferences_that_are_set():
    assert max_score({"energy": 0.5}) == pytest.approx(3.0)
    assert max_score({"genre": "pop", "mood": "happy", "energy": 0.8}) == pytest.approx(6.0)
    assert max_score({}) == 0.0


def test_no_song_can_beat_the_profile_maximum(songs):
    profile = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.2}
    for song in songs:
        assert score_song(profile, song)[0] <= max_score(profile) + 1e-9


def test_numeric_closeness_formula_matches_the_recipe():
    song = {"mood": "x", "genre": "y", "energy": 0.6, "acousticness": 0.5}
    score, _ = score_song({"energy": 0.9, "acousticness": 0.3}, song)
    expected = 3.0 * (1 - abs(0.6 - 0.9)) + 1.0 * (1 - abs(0.5 - 0.3))
    assert score == pytest.approx(expected)


def test_profile_conversion_maps_acoustic_preference():
    acoustic = UserProfile("pop", "happy", 0.5, likes_acoustic=True)
    electronic = UserProfile("pop", "happy", 0.5, likes_acoustic=False)
    assert recommender._profile_to_prefs(acoustic)["acousticness"] > 0.5
    assert recommender._profile_to_prefs(electronic)["acousticness"] < 0.5


# ---------------------------------------------------------------------------
# Phase 3: load, score, rank, CLI output
# ---------------------------------------------------------------------------

def test_load_songs_returns_one_dict_per_csv_row(songs):
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        row_count = sum(1 for _ in csv.DictReader(f))
    assert len(songs) == row_count
    assert all(isinstance(s, dict) for s in songs)


def test_load_songs_can_do_math_on_numeric_fields(songs):
    assert sum(s["energy"] for s in songs) / len(songs) > 0
    assert all(isinstance(s["tempo_bpm"], float) for s in songs)


def test_load_songs_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_songs("data/does_not_exist.csv")


def test_score_song_returns_score_and_list_of_reasons(songs):
    score, reasons = score_song({"genre": "pop", "mood": "happy", "energy": 0.8}, songs[0])
    assert isinstance(score, float)
    assert isinstance(reasons, list)
    assert all(isinstance(r, str) for r in reasons)


def test_recommend_songs_returns_song_score_explanation_tuples(songs):
    results = recommend_songs({"genre": "pop", "mood": "happy", "energy": 0.8}, songs, k=3)
    for song, score, explanation in results:
        assert isinstance(song, dict)
        assert isinstance(score, float)
        assert isinstance(explanation, str) and explanation


def test_recommend_songs_default_k_is_five(songs):
    assert len(recommend_songs({"energy": 0.5}, songs)) == 5


def test_recommend_songs_default_profile_ranks_sunrise_city_first(songs):
    profile = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.2}
    assert top_titles(profile, songs)[0] == "Sunrise City"


def test_oop_recommender_matches_functional_ranking(songs):
    catalog = [
        Song(
            id=s["id"], title=s["title"], artist=s["artist"], genre=s["genre"],
            mood=s["mood"], energy=s["energy"], tempo_bpm=s["tempo_bpm"],
            valence=s["valence"], danceability=s["danceability"],
            acousticness=s["acousticness"],
        )
        for s in songs
    ]
    user = UserProfile("pop", "happy", 0.8, likes_acoustic=False)
    oop = [s.title for s in Recommender(catalog).recommend(user, k=5)]
    prefs = recommender._profile_to_prefs(user)
    functional = top_titles(prefs, songs)
    assert oop == functional


def test_format_recommendations_shows_title_score_and_reasons(songs):
    profile = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.2}
    recs = recommend_songs(profile, songs, k=2)
    text = cli.format_recommendations(profile, recs)
    assert "Sunrise City" in text
    assert "Score:" in text
    assert "mood match" in text
    assert "genre match" in text
    assert "/ 7.00" in text


def test_format_recommendations_numbers_the_results(songs):
    profile = {"energy": 0.5}
    text = cli.format_recommendations(profile, recommend_songs(profile, songs, k=3))
    for rank in ("1. ", "2. ", "3. "):
        assert rank in text
    assert "/ 3.00" in text


def test_format_recommendations_warns_when_nothing_fits(songs):
    profile = {"genre": "k-pop", "mood": "bubbly", "energy": 0.8}
    text = cli.format_recommendations(profile, recommend_songs(profile, songs, k=5))
    assert "WARNING" in text


def test_format_recommendations_no_warning_for_good_match(songs):
    profile = cli.STANDARD_PROFILES["Chill Lofi"]
    text = cli.format_recommendations(profile, recommend_songs(profile, songs, k=5))
    assert "WARNING" not in text


def test_main_prints_loaded_count_and_every_profile(capsys, monkeypatch):
    monkeypatch.chdir(ROOT)
    cli.main()
    out = capsys.readouterr().out
    assert "Loaded songs: 20" in out
    for name in list(cli.STANDARD_PROFILES) + list(cli.ADVERSARIAL_PROFILES):
        assert name in out


# ---------------------------------------------------------------------------
# Phase 4: stress tests, experiment, and the fix
# ---------------------------------------------------------------------------

def test_at_least_three_standard_profiles_defined():
    assert len(cli.STANDARD_PROFILES) >= 3


def test_adversarial_profiles_include_a_conflicting_one():
    assert any("Conflicting" in name for name in cli.ADVERSARIAL_PROFILES)


def test_every_profile_returns_five_results(songs):
    for name, profile in {**cli.STANDARD_PROFILES, **cli.ADVERSARIAL_PROFILES}.items():
        assert len(recommend_songs(profile, songs, k=5)) == 5, name


def test_standard_profiles_have_disjoint_top_fives_at_the_extremes(songs):
    lofi = set(top_titles(cli.STANDARD_PROFILES["Chill Lofi"], songs))
    rock = set(top_titles(cli.STANDARD_PROFILES["Deep Intense Rock"], songs))
    pop = set(top_titles(cli.STANDARD_PROFILES["High-Energy Pop"], songs))
    assert lofi.isdisjoint(rock)
    assert lofi.isdisjoint(pop)


def test_standard_profiles_have_expected_winners(songs):
    expected = {
        "High-Energy Pop": "Sunrise City",
        "Chill Lofi": "Library Rain",
        "Deep Intense Rock": "Storm Runner",
    }
    for name, winner in expected.items():
        assert top_titles(cli.STANDARD_PROFILES[name], songs)[0] == winner, name


def test_chill_lofi_top_results_are_low_energy(songs):
    results = recommend_songs(cli.STANDARD_PROFILES["Chill Lofi"], songs, k=4)
    assert all(song["energy"] < 0.5 for song, _, _ in results)


def test_rock_top_results_are_high_energy(songs):
    results = recommend_songs(cli.STANDARD_PROFILES["Deep Intense Rock"], songs, k=5)
    assert all(song["energy"] > 0.8 for song, _, _ in results)


def test_unknown_genre_and_mood_fall_back_on_energy(songs):
    profile = cli.ADVERSARIAL_PROFILES["Genre and mood not in catalog"]
    results = recommend_songs(profile, songs, k=5)
    assert all(abs(song["energy"] - 0.8) < 0.15 for song, _, _ in results)


def test_energy_only_profile_ranks_by_energy_closeness(songs):
    results = recommend_songs({"energy": 0.5}, songs, k=5)
    gaps = [abs(song["energy"] - 0.5) for song, _, _ in results]
    assert gaps == sorted(gaps)


def test_acoustic_conflict_no_longer_returns_a_quiet_song_first(songs):
    profile = cli.ADVERSARIAL_PROFILES["Conflicting: high-energy but fully acoustic"]
    first_song = recommend_songs(profile, songs, k=1)[0][0]
    assert first_song["energy"] > 0.8


def test_sad_high_energy_profile_scores_low_relative_to_maximum(songs):
    profile = cli.ADVERSARIAL_PROFILES["Conflicting: sad but high-energy"]
    best = recommend_songs(profile, songs, k=1)[0][1]
    assert best < cli.LOW_CONFIDENCE * max_score(profile) + 1e-9


def test_tolerance_rule_constants_are_sensible():
    assert 0 < recommender.ENERGY_TOLERANCE < 1
    assert 0 < recommender.FAR_LABEL_SCALE < 1


def test_tolerance_rule_boundary_is_not_penalized():
    prefs = {"mood": "happy", "energy": 0.5}
    song = {"mood": "happy", "genre": "pop", "energy": 0.8, "acousticness": 0.2}
    score, reasons = score_song(prefs, song)  # gap 0.30 == tolerance
    assert not any("reduced" in r for r in reasons)
    assert score == pytest.approx(2.0 + 3.0 * 0.7)


def test_weight_shift_experiment_keeps_the_math_valid(songs, monkeypatch):
    monkeypatch.setattr(recommender, "ENERGY_WEIGHT", 6.0)
    monkeypatch.setattr(recommender, "GENRE_WEIGHT", 0.5)
    profile = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.2}
    assert max_score(profile) == pytest.approx(9.5)
    for song in songs:
        assert score_song(profile, song)[0] <= 9.5 + 1e-9


def test_weight_shift_experiment_keeps_standard_winners(songs, monkeypatch):
    before = {n: top_titles(p, songs)[0] for n, p in cli.STANDARD_PROFILES.items()}
    monkeypatch.setattr(recommender, "ENERGY_WEIGHT", 6.0)
    monkeypatch.setattr(recommender, "GENRE_WEIGHT", 0.5)
    after = {n: top_titles(p, songs)[0] for n, p in cli.STANDARD_PROFILES.items()}
    assert before == after


def test_genre_weight_zero_does_not_change_standard_winners(songs, monkeypatch):
    before = {n: top_titles(p, songs)[0] for n, p in cli.STANDARD_PROFILES.items()}
    monkeypatch.setattr(recommender, "GENRE_WEIGHT", 0.0)
    after = {n: top_titles(p, songs)[0] for n, p in cli.STANDARD_PROFILES.items()}
    assert before == after


def test_loud_songs_show_up_in_many_profiles(songs):
    """Documents the known bias: the same high-energy songs fill many lists."""
    profiles = {**cli.STANDARD_PROFILES, **cli.ADVERSARIAL_PROFILES}
    appearances = {}
    for profile in profiles.values():
        for title in top_titles(profile, songs):
            appearances[title] = appearances.get(title, 0) + 1
    assert appearances["Fuego en la Calle"] >= 4
    assert appearances["Gym Hero"] >= 4


# ---------------------------------------------------------------------------
# Phase 5: documentation
# ---------------------------------------------------------------------------

def _public_functions():
    for name, obj in inspect.getmembers(recommender, inspect.isfunction):
        if obj.__module__ == recommender.__name__:
            yield name, obj
    for _, cls in inspect.getmembers(recommender, inspect.isclass):
        if cls.__module__ == recommender.__name__:
            for name, obj in inspect.getmembers(cls, inspect.isfunction):
                if not name.startswith("__"):
                    yield f"{cls.__name__}.{name}", obj


def test_every_function_in_recommender_has_a_docstring():
    missing = [name for name, fn in _public_functions() if not (fn.__doc__ or "").strip()]
    assert missing == []


def test_every_function_in_main_has_a_docstring():
    for fn in (cli.format_recommendations, cli.run_profile, cli.main):
        assert (fn.__doc__ or "").strip(), fn.__name__


def test_readme_documents_the_plan_and_results():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    for heading in (
        "How The System Works",
        "Algorithm Recipe",
        "Data Flow",
        "Sample Recommendation Output",
        "Experiments You Tried",
        "Expected Biases and Limitations",
    ):
        assert heading in text, heading
    assert "```" in text


def test_model_card_has_all_nine_sections_filled_in():
    text = (ROOT / "model_card.md").read_text(encoding="utf-8")
    for number in range(1, 10):
        assert f"## {number}. " in text, number
    assert "VibeMatch" in text
    assert "Prompts:" not in text
    assert "Give your model a short" not in text
