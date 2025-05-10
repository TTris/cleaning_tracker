import os
import jwt
from dotenv import load_dotenv
from flask import request, jsonify

load_dotenv()

def get_user_id():
     # 藉由headers的authorization攜帶的bearer, decode jwt, 取得存放在supabase的userid   
     try:
          token = request.headers.get("Authorization").replace("Bearer ","")
          payload = jwt.decode(token, os.getenv("SUPABASE_JWT_SECRET"), algorithms=["HS256"],audience="authenticated")
          return payload.get("sub")
     except Exception as e:
          print("JWT解碼錯誤：",e)
          return None

def require_auth(func):
    def wrapper(*args, **kwargs):
        user_id = get_user_id()
        if not user_id:
             return jsonify({"error":"Unauthorized"}), 401
        return func(user_id=user_id, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper 
