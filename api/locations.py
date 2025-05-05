from flask import Flask, request, jsonify
from db import get_db_conn
from auth import require_auth

app = Flask(__name__)

@app.route("/api/locations", methods=["GET", "POST"])
@require_auth
def handle_locations(user_id):
    conn = get_db_conn()
    cur = conn.cursor()

    if request.method == "GET":
        cur.execute("SELECT id, name FROM locations WHERE user_id = %s", (user_id,))
        rows = cur.fetchall()
        return jsonify([{"id": r[0], "name": r[1]} for r in rows])

    elif request.method == "POST":
        data = request.get_json()
        cur.execute("INSERT INTO locations (user_id, name) VALUES (%s, %s) RETURNING id",
                    (user_id, data["name"]))
        new_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({"id": new_id, "name": data["name"]})
