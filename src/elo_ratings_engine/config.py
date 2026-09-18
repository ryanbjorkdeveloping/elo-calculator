"""
Config values for the Elo rating system
Constants will be defined here through application. Constants may be changed depending on what is being ranked
"""

import os
from dotenv import load_dotenv
import pandas as pd

K_FACTOR = 32
K_FACTOR_MIN = 16
K_FACTOR_MAX = 64

DECAY_HALF_LIFE = 30  # days

S_WIN = 1
S_LOSS = 0

MIN = 1000
MAX = 2200
START_RATING = 1500

FACTOR_WEIGHTS: dict[str, tuple[float, bool]] = {
    # ── Hitting efficiency (most predictive of winning) ──────────────────
    "Avg_Hitting_Pct":          (0.20, True),   # team average — consistency
    "Top_Hitting_Pct":          (0.08, True),   # best hitter ceiling
    "Players_in_HP_Top100":     (0.04, True),   # roster depth in hitting
    # ── Kills (offensive output) ─────────────────────────────────────────
    "Avg_Kills_Per_Set":        (0.13, True),
    "Top_Kills_Per_Set":        (0.05, True),
    "Players_in_KS_Top100":     (0.03, True),
    # ── Assists / setter (system execution) ──────────────────────────────
    "Avg_Assists_Per_Set":      (0.07, True),
    "Top_Assists_Per_Set":      (0.03, True),
    # ── Blocks (net dominance / defense) ─────────────────────────────────
    "Avg_Blocks_Per_Set":       (0.09, True),
    "Top_Blocks_Per_Set":       (0.03, True),
    "Players_in_BS_Top100":     (0.02, True),
    # ── Digs (back-row defense) ───────────────────────────────────────────
    "Avg_Digs_Per_Set":         (0.05, True),
    "Players_in_DS_Top100":     (0.02, True),
    # ── NCAA official rankings (lower rank number = better → inverted) ───
    "AVCA_Rank":                (0.10, False),  # coaches poll
    "RPI_Rank":                 (0.06, False),  # strength-of-schedule
    # ── Win-rate factors (activated when rankings CSV is loaded) ─────────
    "Win_Pct":                  (0.05, True),
    "Conf_Win_Pct":             (0.05, True),
}

TIER_THRESHOLDS = [
    (1800, "Elite"),
    (1650, "Contender"),
    (1500, "Competitive"),
    (1350, "Developing"),
    (0,    "Rebuilding"),
]