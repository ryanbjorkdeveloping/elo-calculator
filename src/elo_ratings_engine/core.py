# expected_score(), apply_update(), predict_match(), RatingSystem class

import math
import logging
from datetime import datetime

import pandas as pd

from elo_ratings_engine.config import (
    K_FACTOR,
    K_FACTOR_MIN,
    K_FACTOR_MAX,
    DECAY_HALF_LIFE,
    S_WIN,
    S_LOSS,
    MIN,
    MAX,
    START_RATING,
    FACTOR_WEIGHTS,
    TIER_THRESHOLDS
)

from elo_ratings_engine.kfactor import (
    margin_multiplier,
    quality_multiplier,
    recency_weight,
    total_weight
)

from elo_ratings_engine.tiers import tier_from_rating

from elo_ratings_engine.seeding import minmax_normalize, weighted_composite, composite_to_minmax


class RatingSystem:

    def __init__(self, k_factor: int = K_FACTOR):
        self.k_factor = k_factor
        self.ratings = {}  # Dictionary to hold team ratings

    def expected_score(self, rating_a: float, rating_b: float) -> float:
        """
        Calculate the expected score for team A against team B using the Elo formula.
        """
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    def apply_update(self, team_a: str, team_b: str, score_a: int, score_b: int, match_date: datetime):
        """
        Update the ratings of two teams after a match.
        """
        rating_a = self.ratings.get(team_a, START_RATING)
        rating_b = self.ratings.get(team_b, START_RATING)

        expected_a = self.expected_score(rating_a, rating_b)
        expected_b = self.expected_score(rating_b, rating_a)

        actual_a = S_WIN if score_a > score_b else S_LOSS
        actual_b = S_WIN if score_b > score_a else S_LOSS

        margin_mult = margin_multiplier(abs(score_a - score_b), max(score_a, score_b), score_a + score_b)
        if actual_a == S_WIN:
            quality_mult = quality_multiplier(r_loser=rating_b, r_winner=rating_a)
        else:
            quality_mult = quality_multiplier(r_loser=rating_a, r_winner=rating_b)
        recency_mult = recency_weight(match_date, datetime.now())
        
        total_mult = total_weight(margin_mult, quality_mult, recency_mult)

        k_adjusted = self.k_factor * total_mult

        new_rating_a = rating_a + k_adjusted * (actual_a - expected_a)
        new_rating_b = rating_b + k_adjusted * (actual_b - expected_b)

        # Ensure ratings stay within bounds
        new_rating_a = max(MIN, min(MAX, new_rating_a))
        new_rating_b = max(MIN, min(MAX, new_rating_b))

        self.ratings[team_a] = new_rating_a
        self.ratings[team_b] = new_rating_b