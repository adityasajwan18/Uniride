# =====================================================
# MERGE SORT ALGORITHM
# Used for ride sorting
# =====================================================

def merge_sort_rides(rides: list, key: str = "distance") -> list:
    """
    Stable O(n log n) sort over ride dictionaries.
    Primary key  : distance (shorter is better)
    Secondary key: time_score (higher is better — negated for sort)
    This gives greedy a better-ordered input to work from.
    """
    if len(rides) <= 1:
        return rides

    mid   = len(rides) // 2
    left  = merge_sort_rides(rides[:mid],  key)
    right = merge_sort_rides(rides[mid:], key)
    return _merge(left, right, key)


def _sort_key(ride: dict, key: str) -> tuple:
    """Composite sort key: (distance ASC, time_score DESC)."""
    return (
        ride.get(key, float("inf")),
        -ride.get("time_score", 0),   # negate so higher time_score sorts first
    )


def _merge(left, right, key):
    merged = []
    i = j  = 0
    while i < len(left) and j < len(right):
        if _sort_key(left[i], key) <= _sort_key(right[j], key):
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged