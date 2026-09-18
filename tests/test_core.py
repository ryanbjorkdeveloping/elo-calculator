from datetime import datetime

import pytest

from elo_ratings_engine.core import RatingSystem
from elo_ratings_engine.kfactor import margin_multiplier, quality_multiplier, recency_weight, total_weight
from elo_ratings_engine.config import S_WIN, S_LOSS, MIN, MAX, START_RATING


# ── expected_score() ──────────────────────────────────────────────────────

def test_expected_score_equal_ratings_is_half():
    system = RatingSystem()
    assert system.expected_score(1500, 1500) == pytest.approx(0.5)


def test_expected_score_symmetric():
    system = RatingSystem()
    for rating_a, rating_b in [(1700, 1500), (1000, 2200), (1500, 1501)]:
        ea = system.expected_score(rating_a, rating_b)
        eb = system.expected_score(rating_b, rating_a)
        assert ea + eb == pytest.approx(1.0)


def test_expected_score_matches_standard_elo_table():
    # Well-known reference points for the logistic Elo formula.
    system = RatingSystem()
    assert system.expected_score(1900, 1500) == pytest.approx(0.90909, rel=1e-4)  # +400 favorite
    assert system.expected_score(1500, 1900) == pytest.approx(0.09091, rel=1e-4)  # -400 underdog
    assert system.expected_score(1700, 1500) == pytest.approx(0.75975, rel=1e-4)  # +200


# ── apply_update() wiring: does it correctly combine expected_score + kfactor helpers? ──

def _manual_new_ratings(system, rating_a, rating_b, score_a, score_b, match_date):
    """Reimplements apply_update's math using the already-verified kfactor
    helper functions, to confirm apply_update wires them together correctly.
    quality_multiplier is called with the ACTUAL winner/loser ratings, matching
    the fixed core.py logic (previously this was hardcoded to rating_b/rating_a
    regardless of who won -- see test_quality_multiplier_uses_actual_winner)."""
    expected_a = system.expected_score(rating_a, rating_b)
    expected_b = system.expected_score(rating_b, rating_a)

    actual_a = S_WIN if score_a > score_b else S_LOSS
    actual_b = S_WIN if score_b > score_a else S_LOSS

    margin_mult = margin_multiplier(abs(score_a - score_b), max(score_a, score_b), score_a + score_b)
    if actual_a == S_WIN:
        quality_mult = quality_multiplier(r_loser=rating_b, r_winner=rating_a)
    else:
        quality_mult = quality_multiplier(r_loser=rating_a, r_winner=rating_b)
    recency_mult = recency_weight(match_date, datetime.now())
    total_mult = total_weight(margin_mult, quality_mult, recency_mult)

    k_adjusted = system.k_factor * total_mult

    new_a = max(MIN, min(MAX, rating_a + k_adjusted * (actual_a - expected_a)))
    new_b = max(MIN, min(MAX, rating_b + k_adjusted * (actual_b - expected_b)))
    return new_a, new_b


def test_apply_update_new_teams_default_to_start_rating():
    system = RatingSystem()
    assert system.ratings == {}
    system.apply_update("TeamA", "TeamB", 3, 0, datetime.now())
    assert "TeamA" in system.ratings
    assert "TeamB" in system.ratings
    # Both started at START_RATING, so the winner's new rating should be above it
    # and the loser's below it.
    assert system.ratings["TeamA"] > START_RATING
    assert system.ratings["TeamB"] < START_RATING


def test_apply_update_favorite_wins_matches_manual_computation():
    system = RatingSystem()
    system.ratings["TeamA"] = 1700
    system.ratings["TeamB"] = 1500
    match_date = datetime.now()

    expected_a, expected_b = _manual_new_ratings(system, 1700, 1500, 3, 1, match_date)
    system.apply_update("TeamA", "TeamB", 3, 1, match_date)

    assert system.ratings["TeamA"] == pytest.approx(expected_a)
    assert system.ratings["TeamB"] == pytest.approx(expected_b)


def test_apply_update_underdog_wins_matches_manual_computation():
    system = RatingSystem()
    system.ratings["TeamA"] = 1700
    system.ratings["TeamB"] = 1500
    match_date = datetime.now()

    # TeamB (lower rated) wins this time -- this is the case that used to be
    # computed wrong before the quality_multiplier fix.
    expected_a, expected_b = _manual_new_ratings(system, 1700, 1500, 1, 3, match_date)
    system.apply_update("TeamA", "TeamB", 1, 3, match_date)

    assert system.ratings["TeamA"] == pytest.approx(expected_a)
    assert system.ratings["TeamB"] == pytest.approx(expected_b)


# ── Rating bounds enforcement ─────────────────────────────────────────────

def test_apply_update_clamps_to_min_rating():
    system = RatingSystem()
    system.ratings["TeamA"] = 1000  # already at MIN
    system.ratings["TeamB"] = 1500
    match_date = datetime.now()

    # TeamA loses again -- unclamped math would push it below MIN.
    unclamped_a = 1000 + (
        system.k_factor
        * total_weight(
            margin_multiplier(3, 3, 3),
            quality_multiplier(r_loser=1000, r_winner=1500),
            recency_weight(match_date, datetime.now()),
        )
        * (S_LOSS - system.expected_score(1000, 1500))
    )
    assert unclamped_a < MIN  # sanity check that the clamp is actually needed here

    system.apply_update("TeamA", "TeamB", 0, 3, match_date)
    assert system.ratings["TeamA"] == pytest.approx(MIN)


def test_apply_update_clamps_to_max_rating():
    system = RatingSystem()
    system.ratings["TeamA"] = 2200  # already at MAX
    system.ratings["TeamB"] = 1000
    match_date = datetime.now()

    unclamped_a = 2200 + (
        system.k_factor
        * total_weight(
            margin_multiplier(3, 3, 3),
            quality_multiplier(r_loser=1000, r_winner=2200),
            recency_weight(match_date, datetime.now()),
        )
        * (S_WIN - system.expected_score(2200, 1000))
    )
    assert unclamped_a > MAX  # sanity check that the clamp is actually needed here

    system.apply_update("TeamA", "TeamB", 3, 0, match_date)
    assert system.ratings["TeamA"] == pytest.approx(MAX)


# ── quality_multiplier now uses the ACTUAL winner/loser, not a hardcoded role ──
# Previously apply_update() always called quality_multiplier(rating_b, rating_a),
# regardless of who won, which backwards-dampened upset wins instead of
# rewarding them. This confirms the fix: an underdog win now gets rewarded.

def test_quality_multiplier_uses_actual_winner():
    system = RatingSystem()
    system.ratings["TeamA"] = 1700  # favorite
    system.ratings["TeamB"] = 1500  # underdog

    match_date = datetime.now()

    # TeamB (underdog) wins -- an upset -- should gain MORE than it would for
    # an equivalent win as the favorite, because quality_mult > 1 for upsets.
    system.apply_update("TeamA", "TeamB", 1, 3, match_date)
    underdog_gain = system.ratings["TeamB"] - 1500

    system2 = RatingSystem()
    system2.ratings["TeamA"] = 1500
    system2.ratings["TeamB"] = 1500
    system2.apply_update("TeamA", "TeamB", 1, 3, match_date)
    neutral_gain = system2.ratings["TeamB"] - 1500

    assert underdog_gain > neutral_gain  # the upset is rewarded, not dampened


if __name__ == "__main__":
    system = RatingSystem()
    print("expected_score(1500, 1500):", system.expected_score(1500, 1500))
    print("expected_score(1900, 1500):", system.expected_score(1900, 1500))

    now = datetime.now()
    system.apply_update("TeamA", "TeamB", 3, 0, now)
    print("\nAfter TeamA beats TeamB 3-0 (both started at 1500):")
    print(system.ratings)
