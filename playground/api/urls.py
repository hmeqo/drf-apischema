from django.urls import include, path
from rest_framework.routers import DefaultRouter

from drf_apischema.urls import api_docs_path

from .views import *

router = DefaultRouter()
router.register("users", UserViewSet)


urlpatterns = [
    path("api/", include(router.urls)),
    # Auto-generate /api-docs/xxx, include /api-docs/scalar/
    api_docs_path(),
]
