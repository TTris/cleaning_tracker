import unittest
from index import app

class BasicTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home_page(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
    
    def test_login_page(self):
        response = self.app.get("/login")
        self.assertEqual(response.status_code, 200)

    def test_reset_password_page(self):
        response = self.app.get("/reset-password")
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()