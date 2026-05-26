# =====================================================
# MERGE SORT ALGORITHM
# Used for ride sorting
# =====================================================

def merge_sort_rides(rides: list, key: str = "distance") -> list:
    """
    Stable O(n log n) sort over ride dictionaries.
    Default key is 'distance' — used after Dijkstra to rank rides
    from shortest to longest route.
    """
    if len(rides) <= 1:
        return rides

    mid = len(rides) // 2
    left = merge_sort_rides(rides[:mid], key)
    right = merge_sort_rides(rides[mid:], key)
    return _merge(left, right, key)


def _merge(left, right, key):
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i].get(key, float("inf")) <= right[j].get(key, float("inf")):
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged
