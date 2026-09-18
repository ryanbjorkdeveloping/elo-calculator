import pandas as pd

from elo_ratings_engine.seeding import (
    minmax_normalize,
    weighted_composite,
    composite_to_minmax,
)

# Sample dataset for hand-checking seeding.py against known values.
# Includes every stat referenced in FACTOR_WEIGHTS, 5 teams, and one
# tied column (RPI_Rank) to exercise the hi == lo branch.
SAMPLE_DF = pd.DataFrame(
    {
        "Team": ["Aces", "Blockers", "Cyclones", "Diggers", "Eagles"],
        "Avg_Hitting_Pct":      [0.320, 0.280, 0.260, 0.300, 0.240],
        "Top_Hitting_Pct":      [0.410, 0.380, 0.350, 0.390, 0.330],
        "Players_in_HP_Top100": [3, 1, 0, 2, 0],
        "Avg_Kills_Per_Set":    [14.2, 12.8, 11.5, 13.6, 10.9],
        "Top_Kills_Per_Set":    [4.8, 4.2, 3.9, 4.5, 3.6],
        "Players_in_KS_Top100": [2, 1, 0, 1, 0],
        "Avg_Assists_Per_Set":  [12.9, 11.7, 10.8, 12.1, 10.2],
        "Top_Assists_Per_Set":  [10.5, 9.8, 8.9, 10.0, 8.4],
        "Avg_Blocks_Per_Set":   [2.6, 2.1, 1.8, 2.3, 1.6],
        "Top_Blocks_Per_Set":   [1.4, 1.1, 0.9, 1.2, 0.8],
        "Players_in_BS_Top100": [1, 0, 0, 1, 0],
        "Avg_Digs_Per_Set":     [15.1, 14.4, 13.9, 14.8, 13.5],
        "Players_in_DS_Top100": [1, 0, 0, 0, 0],
        "AVCA_Rank":            [3, 12, 25, 8, 40],   # lower is better -> inverted
        "RPI_Rank":             [5, 5, 5, 5, 5],       # all tied -> hi == lo
        "Win_Pct":              [0.850, 0.700, 0.550, 0.780, 0.400],
        "Conf_Win_Pct":         [0.900, 0.650, 0.500, 0.750, 0.350],
    }
).set_index("Team")

# Basic minmax testers for minmax_normalize() funtion.
SIMPLE_SERIES = pd.Series([10, 20, 30, 40], index=["A", "B", "C", "D"])
CONSTANT_SERIES = pd.Series([7, 7, 7], index=["X", "Y", "Z"])
SINGLE_ROW_SERIES = pd.Series([42], index=["Solo"])

if __name__ == "__main__":
    print("minmax_normalize(SIMPLE_SERIES):")
    print(minmax_normalize(SIMPLE_SERIES))

    print("\nminmax_normalize(CONSTANT_SERIES):")
    print(minmax_normalize(CONSTANT_SERIES))

    print("\nweighted_composite(SAMPLE_DF):")
    print(weighted_composite(SAMPLE_DF))

    print("\ncomposite_to_minmax(weighted_composite(SAMPLE_DF)):")
    print(composite_to_minmax(weighted_composite(SAMPLE_DF)))
