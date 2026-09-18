from elo_ratings_engine.config import FACTOR_WEIGHTS, MIN, MAX, TIER_THRESHOLDS

def tier_from_rating(rating: float) -> str:
    """
    Determine the tier of a team based on its rating.
    
    Args:
        rating (float): The rating of the team.
        
    Returns:
        str: The tier of the team.
    """
    for threshold, tier in TIER_THRESHOLDS:
        if rating >= threshold:
            return tier
    return "Unknown"  # In case the rating is below all thresholds