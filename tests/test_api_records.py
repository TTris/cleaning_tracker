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
        today = datetime.datetime.now().date().isoformat()
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
    
    def test_get_records(self):
        today = datetime.datetime.now().date().isoformat()
        payload = {
            "location_id": self.location_id,
            "date": today,
            "cleaned": True
        }
        post_response = self.app.post(
            "/api/records",
            headers = {"Authorization": f"Bearer {self.access_token}"},
            data = json.dumps(payload),
            content_type = "application/json"
        )
        self.assertEqual(post_response.status_code, 200)

        get_response = self.app.get(
            "/api/records",
            headers = {"Authorization": f"Bearer {self.access_token}"},
        )
        self.assertEqual(get_response.status_code, 200)
        data = get_response.get_json()
        self.assertTrue(len(data) >= 1)
        self.assertIn("date", data[0])
    
    def test_update_record(self):
        today = datetime.datetime.now().date().isoformat()
        old_response = self.app.post(
            "/api/records",
            headers = {"Authorization": f"Bearer {self.access_token}"},
            data = json.dumps({
                "location_id": self.location_id,
                "date": today,
                "cleaned": True
            }),
            content_type = "application/json"
        )
        self.assertEqual(old_response.status_code, 200)

        new_response = self.app.post(
            "/api/records",
            headers = {"Authorization": f"Bearer {self.access_token}"},
            data = json.dumps({
                "location_id": self.location_id,
                "date": today,
                "cleaned": False
            }),
            content_type = "application/json"
        )
        self.assertEqual(new_response.status_code, 200)

        get_response = self.app.get(
            "/api/records",
            headers = {"Authorization": f"Bearer {self.access_token}"}
        )
        self.assertEqual(get_response.status_code, 200)

        data = get_response.get_json()
        target_rec = [rec for rec in data if rec["date"]==today]
        self.assertTrue(len(target_rec) == 1)
        self.assertEqual(target_rec[0]["location_id"], self.location_id)
        self.assertFalse(target_rec[0]["cleaned"])
