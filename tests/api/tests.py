from django.contrib.auth.models import User
from rest_framework.test import APITestCase

# Create your tests here.


class TestApiSchema(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser("admin", "admin@example.com", "password")

    def test_a(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/test/")
        self.assertEqual(response.json(), [1, 2, 3])

    def test_b(self):
        response = self.client.get("/api/test/square/?n=5")
        self.assertEqual(response.json(), {"result": 25})
