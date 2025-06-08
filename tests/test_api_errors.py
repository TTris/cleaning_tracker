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

def generate_test_token(user_id=None):
    payload = {
        "sub": user_id or str(uuid.uuid4()),
        "aud": "authenticated",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, "test-secret", algorithm="HS256")
    return token

# invalid function return invalid but real JWT
# change return to [return "invalid.jwt.token"] also work for unit test
def generate_invalid_token():
    payload = {
        "sub": str(uuid.uuid4()),
        "aud": "authenticated",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, "wrong-secret", algorithm="HS256")
    return token

class ApiErrorTests(unittest.TestCase):
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
    
    def test_unauthorized_access_no_token(self):
        loc_get_response = self.app.get("/api/locations")
        print(loc_get_response)
        self.assertEqual(loc_get_response.status_code, 401)

        loc_post_response = self.app.post(
            "/api/locations",
            data = json.dumps({"name":"test_location"}),
            content_type = "application/json"
        )
        self.assertEqual(loc_post_response.status_code, 401)

        loc_patch_response = self.app.patch(
            f"/api/locations/{self.location_id}",
            data = json.dumps({"name": "new_location_name"}),
            content_type = "application/json"
        )
        self.assertEqual(loc_patch_response.status_code, 401)

        loc_delete_response = self.app.delete(f"/api/locations/{self.location_id}")
        self.assertEqual(loc_delete_response.status_code, 401)

        rec_get_response = self.app.get("/api/records")
        self.assertEqual(rec_get_response.status_code, 401)

        rec_post_response = self.app.post(
            "/api/records",
            data = json.dumps({
                "location_id": self.location_id,
                "date": datetime.datetime.now().date().isoformat(),
                "cleaned": True
            }),
            content_type = "application/json"
        )
        self.assertEqual(rec_post_response.status_code, 401)
        

    def test_unauthorized_access_invalid_token(self):
        loc_get_response = self.app.get(
            "/api/locations",
            headers = {"Authorization": f"Bearer {generate_invalid_token()}"}
        )
        self.assertEqual(loc_get_response.status_code, 401)

        loc_post_response = self.app.post(
            "/api/locations",
            headers = {"Authorization": f"Bearer {generate_invalid_token()}"},
            data = json.dumps({"name":"test_location"}),
            content_type = "application/json"
        )
        self.assertEqual(loc_post_response.status_code, 401)

        loc_patch_response = self.app.patch(
            f"/api/locations/{self.location_id}",
            headers = {"Authorization": f"Bearer {generate_invalid_token()}"},
            data = json.dumps({"name": "new_location_name"}),
            content_type = "application/json"
        )
        self.assertEqual(loc_patch_response.status_code, 401)

        loc_delete_response = self.app.delete(
            f"/api/locations/{self.location_id}",
            headers = {"Authorization": f"Bearer {generate_invalid_token()}"}
        )
        self.assertEqual(loc_delete_response.status_code, 401)

        rec_get_response = self.app.get(
            "/api/records",
            headers = {"Authorization": f"Bearer {generate_invalid_token()}"}
        )
        self.assertEqual(rec_get_response.status_code, 401)

        rec_post_response = self.app.post(
            "/api/records",
            headers = {"Authorization": f"Bearer {generate_invalid_token()}"},
            data = json.dumps({
                "location_id": self.location_id,
                "date": datetime.datetime.now().date().isoformat(),
                "cleaned": True
            }),
            content_type = "application/json"
        )
        self.assertEqual(rec_post_response.status_code, 401)

    def test_create_location_invalid_payload(self):
        response = self.app.post(
            "/api/locations",
            headers = {"Authorization": f"Bearer {self.access_token}"},
            data = json.dumps({"wrong_field": "test_location"}),
            content_type = "application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_create_record_invalid_payload(self):
        response = self.app.post(
            "/api/records",
            headers = {"Authorization": f"Bearer {self.access_token}"},
            data = json.dumps({"wrong_field": "test_record"}),
            content_type = "application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_nonexistent_location(self):
        fake_id = str(uuid.uuid4())
        response = self.app.delete(
            f"/api/locations/{fake_id}",
            headers = {"Authorization": f"Bearer {self.access_token}"},
        )
        self.assertEqual(response.status_code, 404)

    def test_get_only_own_locations_and_records(self):
        user_a_id = "11111111-1111-1111-1111-111111111111"
        user_b_id = "22222222-2222-2222-2222-222222222222"

        user_a_token = generate_test_token(user_a_id)
        user_b_token = generate_test_token(user_b_id)
        
        # user A create location
        response_a_post_location = self.app.post(
            "/api/locations",
            headers = {"Authorization": f"Bearer {user_a_token}"},
            data = json.dumps({"name": "A's Location"}),
            content_type = "application/json"
        )
        self.assertEqual(response_a_post_location.status_code, 200)

        # user A create record
        location_id_a = response_a_post_location.get_json()["id"]
        response_a_post_record = self.app.post(
            "/api/records",
            headers = {"Authorization": f"Bearer {user_a_token}"},
            data = json.dumps({
                "location_id": location_id_a,
                "date": "2025-05-27",
                "cleaned": True
            }),
            content_type = "application/json"
        )
        self.assertEqual(response_a_post_record.status_code, 200)

        # user B create location
        response_b_post_location = self.app.post(
            "/api/locations",
            headers = {"Authorization": f"Bearer {user_b_token}"},
            data = json.dumps({"name": "B's Location"}),
            content_type = "application/json"
        )
        self.assertEqual(response_b_post_location.status_code, 200)

        # user B create record
        location_id_b = response_b_post_location.get_json()["id"]
        response_b_post_record = self.app.post(
            "/api/records",
            headers = {"Authorization": f"Bearer {user_b_token}"},
            data = json.dumps({
                "location_id": location_id_b,
                "date": "2025-05-28",
                "cleaned": False
            }),
            content_type = "application/json"
        )
        self.assertEqual(response_b_post_record.status_code, 200)

        # user A can only get A's Location not B's location
        response_a_get_location = self.app.get(
            "/api/locations",
            headers = {"Authorization": f"Bearer {user_a_token}"},
        )
        self.assertEqual(response_a_get_location.status_code, 200)
        location_data_a = response_a_get_location.get_json()
        names_a = [loc["name"] for loc in location_data_a]
        self.assertIn("A's Location", names_a)
        self.assertNotIn("B's Location", names_a)

        # user A can only get A's record(2025-05-27) not B's record(2025-05-28)
        response_a_get_record = self.app.get(
            "/api/records",
            headers = {"Authorization": f"Bearer {user_a_token}"}
        )
        self.assertEqual(response_a_get_record.status_code, 200)
        record_data_a = response_a_get_record.get_json()
        dates_a = [rec["date"] for rec in record_data_a]
        self.assertIn("2025-05-27", dates_a)
        self.assertNotIn("2025-05-28", dates_a)
        
if __name__ == "__main__":
    unittest.main()
