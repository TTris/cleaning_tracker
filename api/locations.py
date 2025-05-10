from flask import request, jsonify, Blueprint
from .db import get_db_conn
from .auth import require_auth

locations_bp = Blueprint("locations", __name__)

@locations_bp.route("/api/locations", methods=["GET", "POST"])
@require_auth
def handle_locations(user_id):
    conn = get_db_conn()
    cur = conn.cursor()

    try:
        if request.method == "GET":
            cur.execute("SELECT id, name FROM locations WHERE user_id = %s", (user_id,))
            rows = cur.fetchall()
            return jsonify([{"id": r[0], "name": r[1]} for r in rows])

        elif request.method == "POST":
            data = request.get_json()
            print("data: ", data)
            cur.execute("INSERT INTO locations (user_id, name) VALUES (%s, %s) RETURNING id",
                        (user_id, data["name"]))
            new_id = cur.fetchone()[0]
            conn.commit()
            return jsonify({"id": new_id, "name": data["name"]})
    
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    
    finally:
        cur.close()
        conn.close()

@locations_bp.route("/api/locations/<location_id>", methods=["DELETE", "PATCH"])
@require_auth
def edit_location(user_id, location_id):
    conn = get_db_conn()
    cur = conn.cursor()

    try:
        if request.method == "DELETE":
            cur.execute("""
                DELETE FROM locations
                WHERE id = %s AND user_id = %s
            """, (location_id, user_id))

            if cur.rowcount == 0:
                return jsonify({"error": "Unauthorized or No location found"}), 404
            
            conn.commit()
            return jsonify({"message": "Success"}), 200
        
        elif request.method == "PATCH":
            data = request.get_json()
            new_name = data.get("name", "").strip()

            if not new_name:
                return jsonify({"error": "missing new name"}), 400

            cur.execute("""
                UPDATE locations
                SET name = %s
                WHERE id = %s AND user_id = %s
            """, (new_name, location_id, user_id))

            if cur.rowcount == 0:
                return jsonify({"error":"Unauthorized or No location found"}), 404

            conn.commit()
            return jsonify({"message": "Success"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    
    finally:
        cur.close()
        conn.close()
