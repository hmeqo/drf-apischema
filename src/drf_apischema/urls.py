from __future__ import annotations

from django.urls import URLPattern, URLResolver, include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


def api_path(prefix: str, urlpatterns: list[URLResolver | URLPattern]):
    docs_urlpatterns = [
        path("schema/", SpectacularAPIView.as_view(), name="schema"),
        path("schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]
    return path(prefix, include(docs_urlpatterns + urlpatterns))
