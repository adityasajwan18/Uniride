# =====================================================
# HASHING TECHNIQUE
# Used for fast ride lookup
# =====================================================

class RideHashIndex:
    """
    Hash-table backed indexes over ride records.
    Average lookup complexity: O(1).
    Used to fetch rides by id or by source locality instantly,
    avoiding linear scans over the rides list.
    """

    def __init__(self):
        self._by_id = {}
        self._by_source = {}

    def build(self, rides: list):
        self._by_id.clear()
        self._by_source.clear()
        for ride in rides:
            self._by_id[ride["id"]] = ride
            key = ride["source"].lower().strip()
            self._by_source.setdefault(key, []).append(ride)

    def get_by_id(self, ride_id: int):
        return self._by_id.get(ride_id)

    def get_by_source(self, source: str):
        return self._by_source.get(source.lower().strip(), [])
