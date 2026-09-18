import pandas as pd
from elo_ratings_engine.tiers import tier_from_rating

SAMPLE_ELOS = pd.DataFrame (
    {
        "Team": ["Aces", "Blockers", "Cyclones", "Diggers", "Eagles"],
        "Elo": [1800, 1650, 1500, 1350, 1200],
    }
)

if __name__ == "__main__":
    print("sample elos tier:")
    for index, row in SAMPLE_ELOS.iterrows():
        tier = tier_from_rating(row["Elo"])
        print(f"{row['Team']}: {row['Elo']} - Tier: {tier}")