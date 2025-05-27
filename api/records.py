from flask import request, jsonify, Blueprint
from .db import get_db_conn
from .auth import require_auth
import datetime

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
            # 資料防呆及增加報錯可讀性
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid or missing JSON body"}), 400

            location_id = data.get("location_id", "")
            date = data.get("date", "")
            cleaned = data.get("cleaned")

            errors = []
            if not location_id:
                errors.append("Missing location_id")
            if not date:
                errors.append("Missing date")
            else:
                try:
                    datetime.datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    errors.append("Invalid date format. Expected YYYY-MM-DD")
            if not isinstance(cleaned, bool):
                errors.append("Invalid cleaned value")
            
            if errors:
                return jsonify({"error": errors}), 400

            # 由最後端database決定是INSERT或是UPDATE，不需前端+API分流
            cur.execute("""
                INSERT INTO records (user_id, location_id, date, cleaned)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, location_id, date)
                DO UPDATE SET cleaned = EXCLUDED.cleaned
                RETURNING id    
            """, (user_id, location_id, date, cleaned))
            new_id = cur.fetchone()[0]
            conn.commit()
            return jsonify({"id": new_id, "date": date, "cleaned": cleaned}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()
