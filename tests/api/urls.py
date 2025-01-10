from django.urls import include, path
from rest_framework.routers import DefaultRouter

from drf_apischema.urls import api_path

from .views import *

router = DefaultRouter()
router.register("test", TestViewSet, basename="test")


urlpatterns = [
    # Auto-generate /api/swagger/ and /api/redoc/
    api_path("api/", [path("", include(router.urls))])
]
