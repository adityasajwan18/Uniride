from flask import Flask, request, jsonify, send_from_directory
import json
import os
from datetime import datetime

app = Flask(__name__, static_folder='static')

DATA_FILE = 'data.json'

# ─────────────────────────────────────────────
#  Data helpers
# ─────────────────────────────────────────────

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"owners": [], "finders": []}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ─────────────────────────────────────────────
#  DAA ALGORITHM 1: Greedy Ride Matching
#  Match finders to owners based on:
#    - Same college  (must match)
#    - Locality similarity (scored)
#    - Time proximity (scored)
#  Returns top matches sorted by score
# ─────────────────────────────────────────────

def time_to_minutes(t):
    """Convert HH:MM string to total minutes."""
    try:
        h, m = map(int, t.split(':'))
        return h * 60 + m
    except:
        return 0

def locality_score(loc1, loc2):
    """
    Simple word-overlap score between two locality strings.
    DAA concept: String matching / similarity scoring.
    """
    words1 = set(loc1.lower().split())
    words2 = set(loc2.lower().split())
    common = words1 & words2
    if not common:
        return 0
    # Jaccard similarity
    return len(common) / len(words1 | words2)

def time_score(t1, t2, max_diff_minutes=60):
    """
    Score based on how close departure times are.
    DAA concept: Scoring/ranking function.
    """
    diff = abs(time_to_minutes(t1) - time_to_minutes(t2))
    if diff > max_diff_minutes:
        return 0
    return 1 - (diff / max_diff_minutes)

def greedy_match(finder, owners):
    """
    DAA: Greedy algorithm — pick the best local choice at each step.
    Scores each owner and returns top matches sorted by score.
    """
    matches = []
    for owner in owners:
        # Hard constraint: same college
        if owner['college'].lower() != finder['college'].lower():
            continue
        # Skip if no seats
        if int(owner.get('seats', 0)) <= 0:
            continue

        loc = locality_score(finder['locality'], owner['locality'])
        time = time_score(finder['timing'], owner['timing'])

        # Weighted score: locality matters more than time
        score = round((loc * 0.6) + (time * 0.4), 3)

        if score > 0:
            matches.append({
                "owner": owner,
                "score": score,
                "locality_match": round(loc * 100),
                "time_match": round(time * 100)
            })

    # DAA: Sort by score descending (greedy best-first selection)
    matches.sort(key=lambda x: x['score'], reverse=True)
    return matches[:5]  # Return top 5


# ─────────────────────────────────────────────
#  DAA ALGORITHM 2: Merge Sort for ride listing
#  Sort all rides by time for the dashboard
# ─────────────────────────────────────────────

def merge_sort_by_time(rides):
    """
    DAA: Merge Sort — O(n log n) sorting algorithm.
    Sorts ride listings by departure time.
    """
    if len(rides) <= 1:
        return rides

    mid = len(rides) // 2
    left = merge_sort_by_time(rides[:mid])
    right = merge_sort_by_time(rides[mid:])

    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if time_to_minutes(left[i]['timing']) <= time_to_minutes(right[j]['timing']):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ─────────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/rides')
def rides_page():
    return send_from_directory('static', 'rides.html')

@app.route('/api/register-owner', methods=['POST'])
def register_owner():
    data = load_data()
    owner = request.json
    owner['id'] = len(data['owners']) + 1
    owner['registered_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    data['owners'].append(owner)
    save_data(data)
    return jsonify({"success": True, "message": "Vehicle registered successfully!"})

@app.route('/api/find-rides', methods=['POST'])
def find_rides():
    data = load_data()
    finder = request.json
    # Save finder
    finder['id'] = len(data['finders']) + 1
    finder['searched_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    data['finders'].append(finder)
    save_data(data)

    # Run greedy matching algorithm
    matches = greedy_match(finder, data['owners'])
    return jsonify({"success": True, "matches": matches})

@app.route('/api/all-rides', methods=['GET'])
def all_rides():
    data = load_data()
    # Return merge-sorted rides
    sorted_rides = merge_sort_by_time(data['owners'])
    return jsonify({"rides": sorted_rides})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
