from flask import request, jsonify, Blueprint
from .db import get_db_conn
from .auth import require_auth

records_bp = Blueprint("records", __name__)

@records_bp.route("/api/records", methods=["GET", "POST"])
@require_auth
def handle_records(user_id):
    conn = get_db_conn()
    cur = conn.cursor()
    
    try: 
        if request.method == "GET":
            cur.execute("""
                SELECT id, location_id, date, cleaned FROM records
                WHERE user_id = %s
            """, (user_id,))
            rows = cur.fetchall()
            return jsonify([{"id": r[0], "location_id": r[1], "date": str(r[2]), "cleaned": r[3]} for r in rows])

        elif request.method == "POST":
            data = request.get_json()
            location_id = data["location_id"]
            date = data["date"]
            cleaned = data["cleaned"]

            # 由最後端database決定是INSERT或是UPDATE，不需前端+API分流
            cur.execute("""
                INSERT INTO records (user_id, location_id, date, cleaned)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, location_id, date)
                DO UPDATE SET cleaned = EXCLUDED.cleaned
            """, (user_id, location_id, date, cleaned))

            conn.commit()
            return jsonify({"message":"Record Updated"}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()
