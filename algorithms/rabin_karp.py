# =====================================================
# RABIN-KARP STRING MATCHING ALGORITHM
# Used for locality similarity matching
# =====================================================

PRIME = 101
BASE = 256


def _hash(s, length):
    h = 0
    for i in range(length):
        h = (h * BASE + ord(s[i])) % PRIME
    return h


def rabin_karp_search(text: str, pattern: str) -> bool:
    """
    Case-insensitive substring match using Rabin-Karp rolling hash.
    Returns True if `pattern` occurs anywhere in `text`.
    Used to compare a user's typed locality with stored ride sources.
    """
    if not text or not pattern:
        return False

    text = text.lower().strip()
    pattern = pattern.lower().strip()

    n, m = len(text), len(pattern)
    if m > n:
        # Partial match fallback for short queries
        return pattern in text

    pattern_hash = _hash(pattern, m)
    window_hash = _hash(text, m)

    # Precompute BASE^(m-1) % PRIME for rolling
    h = 1
    for _ in range(m - 1):
        h = (h * BASE) % PRIME

    for i in range(n - m + 1):
        if pattern_hash == window_hash:
            if text[i:i + m] == pattern:
                return True
        if i < n - m:
            window_hash = (BASE * (window_hash - ord(text[i]) * h) +
                           ord(text[i + m])) % PRIME
            if window_hash < 0:
                window_hash += PRIME
    return False


def match_locality(user_input: str, ride_source: str) -> bool:
    """High-level wrapper used by the ride finder."""
    return (rabin_karp_search(ride_source, user_input) or
            rabin_karp_search(user_input, ride_source))


def suggest_locations(user_input: str, all_locations: list) -> list:
    """
    Return locations from all_locations whose name contains user_input
    (Rabin-Karp substring search). Used for live autocomplete.
    """
    if not user_input or not user_input.strip():
        return all_locations
    return [loc for loc in all_locations
            if rabin_karp_search(loc, user_input.strip())]