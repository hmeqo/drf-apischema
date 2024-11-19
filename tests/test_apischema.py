from django.test import override_settings
from django.urls import include, path
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.routers import DefaultRouter
from rest_framework.test import APITestCase
from rest_framework.viewsets import ViewSet

from drf_apischema import apischema
from drf_apischema.utils import api_path


class AOut(serializers.ListSerializer):
    child = serializers.IntegerField()


class BQuery(serializers.Serializer):
    n = serializers.IntegerField(default=2)


class AViewSet(ViewSet):
    @apischema(response=AOut)
    def list(self, request):
        return [1, 2, 3]


@api_view(["GET"])
@apischema(query=BQuery, transaction=False)
def b_view(request, data: dict):
    n: int = data["n"]
    return n * n


router = DefaultRouter()
router.register("a", AViewSet, basename="a")


urlpatterns = [
    api_path(
        "api/",
        [
            path("", include(router.urls)),
            path("b/", b_view),
        ],
    )
]


@override_settings(ROOT_URLCONF="tests.test_apischema")
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
