from __future__ import annotations

from django.conf import settings
from django.urls import URLPattern, URLResolver, include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from .scalar.views import scalar_viewer


def api_path(
    urlpatterns: list[URLResolver | URLPattern],
    prefix: str = "",
    api_prefix: str = "api/",
    docs_prefix: str = "api-docs/",
):
    docs_urlpatterns = [
        path("schema/", SpectacularAPIView.as_view(), name="schema"),
        path("scalar/", scalar_viewer, name="scalar"),
        path(
            "swagger-ui/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]
    return path(
        prefix,
        include(
            [
                path(api_prefix, include(urlpatterns)),
                path(docs_prefix, include(docs_urlpatterns)),
            ]
        ),
    )
