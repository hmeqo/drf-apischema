from rest_framework.test import APITestCase

# Create your tests here.


class TestApiSchema(APITestCase):
    def test_a(self):
        response = self.client.get("/api/a/")
        self.assertEqual(response.json(), [1, 2, 3])

    def test_b(self):
        response = self.client.get("/api/b/?n=5")
        self.assertEqual(response.json(), 25)

    def test_b_default(self):
        response = self.client.get("/api/b/")
        self.assertEqual(response.json(), 4)
