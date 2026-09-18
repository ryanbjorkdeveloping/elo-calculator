# minmax_normalize(), weighted_composite(), rescale_to_range()

import os
from dotenv import load_dotenv
import pandas as pd
from elo_ratings_engine.config import FACTOR_WEIGHTS, MIN, MAX


"""
How it's going to work:
1) Normalize all the stats in the dataframe to a range of 0-1, where 0 is the minimum value and 1 is the maximum value for each stat. This is done to ensure that all stats are on the same scale and can be compared to each other.
2) For each stat, multiply the normalized value by the weight defined in FACTOR_WEIGHTS
3) Sum all the weighted values for each team to get a composite score
4) Rescale the composite score to a range of MIN-MAX, where MIN is the minimum rating and MAX is the maximum rating. 
This is done to ensure that the composite score is on the same scale as the Elo ratings and can be compared to each other.
"""

# Step 1
# _minmax() normalizes all the stats in the dataframe to a range of 0-1, where 0 is the minimum value and 1 is the maximum value for each stat.
# worst stat is 0 and best stat is 1. This is done to ensure that all stats are on the same scale and can be compared to each other.
def minmax_normalize(series: pd.Series) -> pd.Series:
    lo, hi = series.min(), series.max()
    if hi == lo:
        return pd.Series(0.5, index=series.index)  # If all values are the same, return a series of 0.5
    return (series - lo) / (hi - lo) if hi > lo else series 


# Steps 2-3
# weighted_composite() takes a dataframe of stats and returns a series of composite scores for each team. The composite score is calculated by multiplying each stat by its weight defined in FACTOR_WEIGHTS and summing the weighted values for each team.
def weighted_composite(df: pd.DataFrame) -> pd.Series:
    composite_scores = pd.Series(0, index=df.index)
    for stat, (weight, is_positive) in FACTOR_WEIGHTS.items():
        if stat in df.columns:
            normalized_stat = minmax_normalize(df[stat])
            if not is_positive:
                normalized_stat = 1 - normalized_stat  # Invert the stat if lower is better
            composite_scores += normalized_stat * weight
    return composite_scores

# Step 4
# composite_to_minmax() takes a series of composite scores and returns a series of normalized scores within the range of MIN-MAX.
def composite_to_minmax(composite_scores: pd.Series) -> pd.Series:
    lo, hi = composite_scores.min(), composite_scores.max()
    if hi == lo:
        return pd.Series((MIN + MAX) / 2, index=composite_scores.index)  # If all values are the same, return a series of the midpoint
    return MIN + (composite_scores - lo) * (MAX - MIN) / (hi - lo)

