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

class LocationsApiTests(unittest.TestCase):
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
    
    def test_create_location(self):
        response = self.app.post(
            "/api/locations",
            headers = {"Authorization": f"Bearer {self.access_token}"},
            data = json.dumps({"name": "test_location"}),
            content_type = "application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], "test_location")
    
    def test_get_locations(self):
        self.app.post(
            "/api/locations",
            headers = {"Authorization": f"Bearer {self.access_token}"},
            data = json.dumps({"name": "3F_floor"}),
            content_type = "application/json"
        )

        response = self.app.get(
            "/api/locations",
            headers = {"Authorization": f"Bearer {self.access_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(len(data) >= 1)
        self.assertIn("name", data[0])

if __name__ == "__main__":
    unittest.main()