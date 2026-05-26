# =====================================================
# GREEDY ALGORITHM
# Used for best ride recommendation
# =====================================================

def greedy_best_rides(rides: list, user_source: str) -> list:
    """
    Greedy scoring: at every step prefer the ride that maximizes
    a composite score derived from:
       - shortest distance         (lower is better)
       - seat availability         (higher is better)
       - locality match            (boost if source matches)
    The algorithm repeatedly picks the locally optimal ride until none remain.
    """
    if not rides:
        return []

    user_source = user_source.lower().strip()
    scored = []
    for ride in rides:
        distance = ride.get("distance", 0) or 1
        seats = ride.get("seats", 0)
        locality_boost = 5 if user_source and user_source in ride["source"].lower() else 0
        # Higher score = better ride
        score = (10 / distance) + (seats * 0.8) + locality_boost
        scored.append((score, ride))

    selected = []
    while scored:
        # Greedy pick: highest score every iteration
        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored.pop(0)
        selected.append(best[1])
    return selected
