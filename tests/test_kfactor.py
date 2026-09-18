import math

import pytest

from elo_ratings_engine.kfactor import (
    margin_multiplier,
    quality_multiplier,
    recency_weight,
    total_weight,
)

# DECAY_HALF_LIFE = 30 (from config.py) -> recency_weight = exp(-days_diff / 30)


def test_margin_multiplier_sweep():
    # 3-0 sweep: sets_won=3, total_sets=3 -> set_ratio=1.0 -> 0.5 + 1.0
    assert margin_multiplier(margin=25, sets_won=3, total_sets=3) == pytest.approx(1.5)


def test_margin_multiplier_five_setter():
    # 3-2 win: sets_won=3, total_sets=5 -> set_ratio=0.6 -> 0.5 + 0.6
    assert margin_multiplier(margin=2, sets_won=3, total_sets=5) == pytest.approx(1.1)


def test_margin_multiplier_four_setter():
    # 3-1 win: sets_won=3, total_sets=4 -> set_ratio=0.75 -> 0.5 + 0.75
    assert margin_multiplier(margin=15, sets_won=3, total_sets=4) == pytest.approx(1.25)


def test_margin_multiplier_zero_total_sets_raises():
    # total_sets=0 is a division by zero -- documenting current behavior, not fixing it.
    with pytest.raises(ZeroDivisionError):
        margin_multiplier(margin=0, sets_won=0, total_sets=0)


def test_quality_multiplier_equal_ratings():
    # Same rating -> no gap -> neutral multiplier
    assert quality_multiplier(r_loser=1500, r_winner=1500) == pytest.approx(1.0)


def test_quality_multiplier_upset_win():
    # Winner rated 200 below loser (upset) -> elo_gap=200 -> +0.25
    assert quality_multiplier(r_loser=1700, r_winner=1500) == pytest.approx(1.25)


def test_quality_multiplier_expected_win():
    # Winner rated 200 above loser (expected) -> elo_gap=-200 -> -0.25
    assert quality_multiplier(r_loser=1300, r_winner=1500) == pytest.approx(0.75)


def test_quality_multiplier_clamped_high():
    # Extreme upset: elo_gap=1200 -> would be +1.5, clamped to +0.5
    assert quality_multiplier(r_loser=2200, r_winner=1000) == pytest.approx(1.5)


def test_quality_multiplier_clamped_low():
    # Extreme expected win: elo_gap=-1200 -> would be -1.5, clamped to -0.5
    assert quality_multiplier(r_loser=1000, r_winner=2200) == pytest.approx(0.5)


def test_recency_weight_same_day():
    from datetime import datetime

    same_day = datetime(2026, 9, 17)
    assert recency_weight(same_day, same_day) == pytest.approx(1.0)


def test_recency_weight_30_days():
    from datetime import datetime, timedelta

    current_date = datetime(2026, 9, 17)
    match_date = current_date - timedelta(days=30)
    # DECAY_HALF_LIFE = 30 -> exp(-30/30) = exp(-1)
    assert recency_weight(match_date, current_date) == pytest.approx(math.exp(-1))


def test_recency_weight_60_days():
    from datetime import datetime, timedelta

    current_date = datetime(2026, 9, 17)
    match_date = current_date - timedelta(days=60)
    assert recency_weight(match_date, current_date) == pytest.approx(math.exp(-2))


def test_total_weight_multiplies_all_three():
    assert total_weight(margin_mult=1.1, quality_mult=1.25, recency_mult=0.5) == pytest.approx(0.6875)


def test_total_weight_identity():
    assert total_weight(margin_mult=1.0, quality_mult=1.0, recency_mult=1.0) == pytest.approx(1.0)


if __name__ == "__main__":
    from datetime import datetime, timedelta

    print("margin_multiplier(sweep 3-0):", margin_multiplier(25, 3, 3))
    print("margin_multiplier(5-setter 3-2):", margin_multiplier(2, 3, 5))
    print("margin_multiplier(4-setter 3-1):", margin_multiplier(15, 3, 4))

    print("\nquality_multiplier(equal 1500 vs 1500):", quality_multiplier(1500, 1500))
    print("quality_multiplier(upset, loser=1700 winner=1500):", quality_multiplier(1700, 1500))
    print("quality_multiplier(expected, loser=1300 winner=1500):", quality_multiplier(1300, 1500))
    print("quality_multiplier(clamped high, loser=2200 winner=1000):", quality_multiplier(2200, 1000))
    print("quality_multiplier(clamped low, loser=1000 winner=2200):", quality_multiplier(1000, 2200))

    now = datetime(2026, 9, 17)
    print("\nrecency_weight(same day):", recency_weight(now, now))
    print("recency_weight(30 days ago):", recency_weight(now - timedelta(days=30), now))
    print("recency_weight(60 days ago):", recency_weight(now - timedelta(days=60), now))

    print("\ntotal_weight(1.1, 1.25, 0.5):", total_weight(1.1, 1.25, 0.5))
