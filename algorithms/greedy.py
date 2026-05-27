# =====================================================
# GREEDY ALGORITHM
# Used for best ride recommendation
# =====================================================

from datetime import datetime


def _parse_time_minutes(time_str: str) -> int | None:
    """Convert 'HH:MM:SS' or 'HH:MM' to total minutes since midnight."""
    try:
        parts = time_str.strip().split(":")
        return int(parts[0]) * 60 + int(parts[1])
    except Exception:
        return None


def _time_score(ride_time_str: str) -> float:
    """
    Score a ride based on how close its departure is to current time.
    - Departed already (< now)     : penalty  → score 0.0
    - Departs within 30 min        : best      → score 3.0
    - Departs within 31–60 min     : good      → score 2.0
    - Departs within 61–120 min    : ok        → score 1.0
    - Departs more than 2 hrs away : low       → score 0.3
    """
    ride_minutes = _parse_time_minutes(ride_time_str)
    if ride_minutes is None:
        return 1.0  # unknown time — neutral score

    now = datetime.now()
    now_minutes = now.hour * 60 + now.minute
    diff = ride_minutes - now_minutes  # positive = future, negative = past

    if diff < 0:
        return 0.0    # already departed
    elif diff <= 30:
        return 3.0    # leaving very soon — best
    elif diff <= 60:
        return 2.0    # within the hour — good
    elif diff <= 120:
        return 1.0    # within 2 hours — ok
    else:
        return 0.3    # too far ahead — low priority


def greedy_best_rides(rides: list, user_source: str) -> list:
    """
    Greedy scoring: at every step prefer the ride that maximizes
    a composite score derived from:
       - shortest distance         (lower is better)
       - seat availability         (higher is better)
       - locality match            (boost if source matches)
       - time proximity            (rides departing soon ranked higher)
    The algorithm repeatedly picks the locally optimal ride until none remain.
    """
    if not rides:
        return []

    user_source = user_source.lower().strip()
    scored = []
    for ride in rides:
        distance       = ride.get("distance", 0) or 1
        seats          = ride.get("seats", 0)
        locality_boost = 5 if user_source and user_source in ride["source"].lower() else 0
        time_boost     = _time_score(ride.get("time", ""))

        # Higher score = better ride
        score = (10 / distance) + (seats * 0.8) + locality_boost + (time_boost * 2)
        ride["time_score"] = time_boost  # attach so UI can show it
        scored.append((score, ride))

    selected = []
    while scored:
        # Greedy pick: highest score every iteration
        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored.pop(0)
        selected.append(best[1])
    return selected