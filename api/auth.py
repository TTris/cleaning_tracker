import os
import jwt
from dotenv import load_dotenv
from flask import request, jsonify
from functools import wraps

load_dotenv()

def get_user_id():
     # 藉由headers的authorization攜帶的bearer, decode jwt, 取得存放在supabase的userid   
     try:
          header = request.headers.get("Authorization")
          if (not header) or (not header.startswith("Bearer ")):
               return None
          token = header.split(" ")[1]
          payload = jwt.decode(token, os.getenv("SUPABASE_JWT_SECRET"), algorithms=["HS256"],audience="authenticated")
          return payload.get("sub")

     except Exception as e:
          print("Error", e)
          return None

def require_auth(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        user_id = get_user_id()
        if not user_id:
             return jsonify({"Error": "Unauthorized"}), 401
        return func(user_id=user_id, *args, **kwargs)
    return decorated 
