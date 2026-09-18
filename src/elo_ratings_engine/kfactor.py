# margin_multiplier(), quality_multiplier(), recency_weight(), compute_k()

import math
import logging
from datetime import datetime, timedelta

import pandas as pd

logger = logging.getLogger(__name__)

from elo_ratings_engine.config import (
    K_FACTOR,
    K_FACTOR_MIN,
    K_FACTOR_MAX,
    DECAY_HALF_LIFE
)

def margin_multiplier(margin: int, sets_won: int, total_sets: int) -> float:
    """
    Calculate the margin multiplier based on the margin of victory.
    The multiplier increases with the margin of victory, but at a diminishing rate.
    """
    set_ratio = sets_won / total_sets
    margin_mult = 0.5 + set_ratio
    return margin_mult


def quality_multiplier(r_loser: float, r_winner: float) -> float:
    """
    Calculate the quality multiplier based on the Elo ratings of the winner and loser.
    The multiplier increases when the winner has a lower rating than the loser, indicating an upset.
    """
    elo_gap = r_loser - r_winner
    quality_mult = 1.0 + max(-0.50, min(0.50, elo_gap / 800))
    return quality_mult

def recency_weight(match_date: datetime, current_date: datetime) -> float:
    """
    Calculate the recency weight based on the date of the match and the current date.
    The weight decreases as the time since the match increases.
    """
    time_diff = current_date - match_date
    days_diff = time_diff.days
    recency_weight = math.exp(-days_diff / DECAY_HALF_LIFE)  # Adjust the decay rate as needed
    return recency_weight

def total_weight(margin_mult: float, quality_mult: float, recency_mult: float) -> float:
    """
    Calculate the total weight by multiplying the margin, quality, and recency multipliers.
    """
    return margin_mult * quality_mult * recency_mult


