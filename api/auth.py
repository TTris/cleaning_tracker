import os
import jwt
from flask import request, jsonify

def get_user_id():
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = jwt.decode(token, os.getenv("SUPABASE_JWT_SECRET"), algorithms=["HS256"])
        return payload.get("sub")
    except Exception as e:
        return None

def require_auth(func):
    def wrapper(*args, **kwargs):
        user_id = get_user_id()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401
        return func(user_id=user_id, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper
