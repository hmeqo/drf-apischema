from django.contrib.auth.models import User
from rest_framework.test import APITestCase

# Create your tests here.


class TestApiSchema(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser("admin", "admin@example.com", "password")
        self.user2 = User.objects.create_user("user", "user@example.com", "password")

    def test_a(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/users/")
        self.assertEqual(response.json(), [{"id": 1, "username": "admin"}, {"id": 2, "username": "user"}])

    def test_b(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/users/square/?n=5")
        self.assertEqual(response.json(), {"result": 25})
