from flask import Flask, request, jsonify, Blueprint
from .db import get_db_conn
from .auth import require_auth

records_bp = Blueprint("records", __name__)

@records_bp.route("/api/records", methods=["GET", "POST"])
@require_auth
def handle_records(user_id):
    conn = get_db_conn()
    cur = conn.cursor()

    if request.method == "GET":
        start = request.args.get("start")
        end = request.args.get("end")
        cur.execute("""
            SELECT id, location_id, date, cleaned FROM cleaning_records
            WHERE user_id = %s AND date BETWEEN %s AND %s
        """, (user_id, start, end))
        rows = cur.fetchall()
        return jsonify([{"id": r[0], "location_id": r[1], "date": str(r[2]), "cleaned": r[3]} for r in rows])

    elif request.method == "POST":
        data = request.get_json()
        cur.execute("""
            INSERT INTO cleaning_records (user_id, location_id, date, cleaned)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (user_id, data["location_id"], data["date"], data["cleaned"]))
        new_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({"id": new_id})

# for postman dev purpose, no need for authorization
@records_bp.route("/api/records/dev", methods=["GET", "POST"])
def handle_records_dev():
    conn = get_db_conn()
    cur = conn.cursor()
    data = request.get_json()
    user_id = data["user_id"]

    if request.method == "GET":
        start = request.args.get("start")
        end = request.args.get("end")
        cur.execute("""
            SELECT id, location_id, date, cleaned FROM records
            WHERE user_id = %s AND date BETWEEN %s AND %s
        """, (user_id, start, end))
        rows = cur.fetchall()
        return jsonify([{"id": r[0], "location_id": r[1], "date": str(r[2]), "cleaned": r[3]} for r in rows])

    elif request.method == "POST":
        cur.execute("""
            INSERT INTO records (user_id, location_id, date, cleaned)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (user_id, data["location_id"], data["date"], data["cleaned"]))
        new_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({"id": new_id})