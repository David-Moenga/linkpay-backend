from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_and_login(self):
        r = self.client.post("/api/auth/register/", {
            "username": "alice", "email": "alice@test.com", "password": "Strong!pass123", "account_type": "individual"
        }, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", r.data)
        self.assertEqual(User.objects.count(), 1)

        r2 = self.client.post("/api/auth/login/", {"email": "alice@test.com", "password": "Strong!pass123"}, format="json")
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        self.assertIn("access", r2.data)

    def test_lookup_requires_auth(self):
        r = self.client.get("/api/users/lookup/?q=alice")
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)
