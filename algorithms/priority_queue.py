# =====================================================
# PRIORITY QUEUE
# Used for nearest ride selection
# =====================================================

import heapq


def nearest_rides(rides: list, k: int = 5) -> list:
    """
    Min-heap based extraction of the K best rides using a composite key:
      - primary   : distance (shorter is better)
      - secondary : time_score (sooner departure is better)
      - tertiary  : seats (more seats is better)

    Rides already arrive greedy-ranked; the heap re-confirms the top-K
    using the same signals without discarding the greedy work.
    Time complexity: O(n log k).
    """
    if not rides:
        return []

    heap = []
    for ride in rides:
        distance   =  ride.get("distance",   float("inf"))
        time_score = -ride.get("time_score", 0)   # negate: higher score = better
        seats      = -ride.get("seats",      0)   # negate: more seats = better

        # Min-heap: smallest tuple wins → (short distance, high time_score, many seats)
        heapq.heappush(heap, (distance, time_score, seats, ride["id"], ride))

    result = []
    for _ in range(min(k, len(heap))):
        *_, ride = heapq.heappop(heap)
        result.append(ride)
    return result