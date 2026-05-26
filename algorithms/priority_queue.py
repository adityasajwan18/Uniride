# =====================================================
# PRIORITY QUEUE
# Used for nearest ride selection
# =====================================================

import heapq


def nearest_rides(rides: list, k: int = 5) -> list:
    """
    Min-heap based extraction of the K rides with the shortest distance.
    Time complexity: O(n log k).
    """
    if not rides:
        return []

    heap = []
    for ride in rides:
        heapq.heappush(heap, (ride.get("distance", float("inf")), ride["id"], ride))

    result = []
    for _ in range(min(k, len(heap))):
        _, _, ride = heapq.heappop(heap)
        result.append(ride)
    return result
