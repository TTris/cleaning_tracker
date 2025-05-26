import unittest
import json
from index import app
from api.db import get_db_conn
import jwt
import datetime
import uuid

def check_using_test_db():
    conn = get_db_conn()
    dbname = conn.get_dsn_parameters().get("dbname", "")
    if dbname != "cleaning_test":
        raise RuntimeError(f"⚠️ 危險！當前資料庫為 {dbname}，請確認為「測試資料庫」再執行刪除操作")
    conn.close()

def generate_test_token():
    payload = {
        "sub": str(uuid.uuid4()),
        "aud": "authenticated",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, "test-secret", algorithm="HS256")
    return token

class RecordsApiTests(unittest.TestCase):
    def setUp(self):
        check_using_test_db()
        self.app = app.test_client()
        self.app.testing = True
        self.access_token = generate_test_token()

        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM records")
        cur.execute("DELETE FROM locations")
        conn.commit()
        cur.close()
        conn.close()

        test_location_res = self.app.post(
            "/api/locations",
            headers = {"Authorization": f"Bearer {self.access_token}"},
            data = json.dumps({"name": "test_location"}),
            content_type = "application/json"
        )
        self.location_id = test_location_res.get_json()["id"]

    def test_create_record(self):
        today = str(datetime.datetime.now())[:10]
        payload = {
            "location_id": self.location_id,
            "date": today,
            "cleaned": True
        }
        response = self.app.post(
            "/api/records",
            headers = {"Authorization": f"Bearer {self.access_token}"},
            data = json.dumps(payload),
            content_type = "application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        print(data)
        self.assertIn("id", data)
        self.assertEqual(data["date"], today)
    