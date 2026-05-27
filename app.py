from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error

from algorithms.rabin_karp import match_locality
from algorithms.merge_sort import merge_sort_rides
from algorithms.dijkstra import shortest_route, DEHRADUN_GRAPH
from algorithms.hashing import RideHashIndex
from algorithms.priority_queue import nearest_rides
from algorithms.greedy import greedy_best_rides

app = Flask(__name__)

# ---------- MySQL Config ----------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Adi@18042004",          
    "database": "uniride",
}


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def fetch_all_rides():
    """Pull rides from MySQL, return list of dicts."""
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, driver_name, source, destination, time, seats, distance FROM rides")
        rides = cur.fetchall()
        cur.close(); conn.close()
        # Normalise time field to string
        for r in rides:
            r["time"] = str(r["time"])
        return rides
    except Error as e:
        print("DB error:", e)
        return []


# ============================================================
# Page Routes
# ============================================================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/route")
def route_page():
    return render_template("route.html", graph=DEHRADUN_GRAPH)


# ============================================================
# API: Add Ride
# ============================================================
@app.route("/add-ride", methods=["POST"])
def add_ride():
    data = request.get_json(force=True)
    driver = data.get("driver_name", "").strip()
    source = data.get("source", "").strip()
    destination = data.get("destination", "GEHU").strip()
    time_val = data.get("time", "").strip()
    seats = int(data.get("seats", 1))

    if not (driver and source and time_val):
        return jsonify({"success": False, "message": "Missing required fields."}), 400

    # Pre-compute distance using Dijkstra so the dashboard has it ready
    route_info = shortest_route(source, destination)
    distance = route_info["distance"]

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO rides (driver_name, source, destination, time, seats, distance)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (driver, source, destination, time_val, seats, distance),
        )
        conn.commit()
        ride_id = cur.lastrowid
        cur.close(); conn.close()
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({
        "success": True,
        "message": "Ride added successfully.",
        "ride_id": ride_id,
        "distance": distance,
    })


# ============================================================
# API: Find Rides
# ============================================================
@app.route("/find-rides", methods=["POST"])
def find_rides():
    data = request.get_json(force=True)
    user_source = data.get("source", "").strip()
    destination = data.get("destination", "GEHU").strip()

    if not user_source:
        return jsonify({"success": False, "message": "Source location required."}), 400

    all_rides = fetch_all_rides()
    if not all_rides:
        return jsonify({"success": True, "rides": [], "route": None})

    # 1. Build hash index for O(1) lookups
    index = RideHashIndex()
    index.build(all_rides)

    # 2. Rabin-Karp locality filter
    matched = [r for r in all_rides if match_locality(user_source, r["source"])]
    if not matched:
        matched = all_rides  # fallback so user always sees something

    # 3. Dijkstra — attach optimized route+distance to each ride
    for ride in matched:
        route_info = shortest_route(ride["source"], destination)
        ride["distance"] = route_info["distance"] or ride["distance"]
        ride["path"] = route_info["path"]

    # 4. Merge sort by distance
    sorted_rides = merge_sort_rides(matched, key="distance")

    # 5. Greedy best-ride ranking on the sorted set
    ranked = greedy_best_rides(sorted_rides, user_source)

    # 6. Priority queue — surface top-K nearest
    top_nearest = nearest_rides(ranked, k=5)

    # 7. Best overall route summary (from user's source)
    overall_route = shortest_route(user_source, destination)

    return jsonify({
        "success": True,
        "rides": top_nearest,
        "route": overall_route,
        "algorithms_used": [
            "Rabin-Karp (locality match)",
            "Hashing (O(1) ride index)",
            "Dijkstra (route optimization)",
            "Merge Sort (distance sort)",
            "Greedy (best-ride scoring)",
            "Priority Queue (nearest K)",
        ],
    })


# ============================================================
# API: Dashboard Stats
# ============================================================
@app.route("/stats")
def stats():
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) AS total FROM rides")
        total = cur.fetchone()["total"]
        cur.execute("SELECT COUNT(DISTINCT source) AS routes FROM rides")
        routes = cur.fetchone()["routes"]
        cur.execute("""SELECT id, driver_name, source, destination, time, seats, distance
                       FROM rides ORDER BY created_at DESC LIMIT 6""")
        recent = cur.fetchall()
        for r in recent:
            r["time"] = str(r["time"])
        cur.close(); conn.close()
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({
        "success": True,
        "total_rides": total,
        "active_routes": routes,
        "algorithms_used": 6,
        "recent_rides": recent,
    })


if __name__ == "__main__":
    app.run(debug=True)
