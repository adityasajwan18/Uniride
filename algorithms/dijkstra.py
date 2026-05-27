# =====================================================
# DIJKSTRA SHORTEST PATH ALGORITHM
# Used for route optimization
# =====================================================

import heapq

# Weighted graph of key Dehradun locations (distances in km, approximate)
DEHRADUN_GRAPH = {
    "Kargi Chowk":   {"ISBT": 3, "Subhash Nagar": 5},
    "ISBT":          {"Kargi Chowk": 3, "Subhash Nagar": 2, "Clock Tower": 8},
    "Subhash Nagar": {"ISBT": 2, "Kargi Chowk": 5, "Balliwala": 6, "GEHU": 1},
    "Balliwala":     {"Subhash Nagar": 6, "Prem Nagar": 8, "GEHU": 8},
    "Clock Tower":   {"ISBT": 8, "Prem Nagar": 9},
    "Prem Nagar":    {"Balliwala": 8, "Clock Tower": 9, "GEHU": 3},
    "GEHU":          {"Prem Nagar": 3, "Balliwala": 6, "Subhash Nagar": 1},
}


def dijkstra(graph: dict, source: str, destination: str) -> dict:
    """
    Classic Dijkstra with a min-heap.
    Returns: {"distance": <int>, "path": [nodes...]}
    """
    if source not in graph or destination not in graph:
        return {"distance": 0, "path": []}

    distances = {node: float("inf") for node in graph}
    previous = {node: None for node in graph}
    distances[source] = 0

    pq = [(0, source)]
    visited = set()

    while pq:
        current_dist, current = heapq.heappop(pq)
        if current in visited:
            continue
        visited.add(current)

        if current == destination:
            break

        for neighbour, weight in graph[current].items():
            new_dist = current_dist + weight
            if new_dist < distances[neighbour]:
                distances[neighbour] = new_dist
                previous[neighbour] = current
                heapq.heappush(pq, (new_dist, neighbour))

    # Reconstruct path
    path, node = [], destination
    while node is not None:
        path.insert(0, node)
        node = previous[node]

    if not path or path[0] != source:
        return {"distance": 0, "path": []}

    return {"distance": distances[destination], "path": path}


def shortest_route(source: str, destination: str = "GEHU") -> dict:
    return dijkstra(DEHRADUN_GRAPH, source, destination)
