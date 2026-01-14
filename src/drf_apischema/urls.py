from __future__ import annotations

from django.urls import URLPattern, URLResolver, include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from .scalar.views import scalar_viewer
from .settings import api_settings


def api_docs_path(
    prefix: str = "api-docs/",
    extra_urlpatterns: list[URLPattern | URLResolver] | None = None,
    openapi_url_name: str | None = None,
):
    openapi_url_name = openapi_url_name or api_settings.OPENAPI_URL_NAME

    docs_urlpatterns: list[URLPattern | URLResolver] = [
        path(f"{openapi_url_name}/", SpectacularAPIView.as_view(), name=openapi_url_name),
        path("scalar/", scalar_viewer, name="scalar", kwargs={"url_name": openapi_url_name}),
        path(
            "swagger-ui/",
            SpectacularSwaggerView.as_view(url_name=openapi_url_name),
            name="swagger-ui",
        ),
        path("redoc/", SpectacularRedocView.as_view(url_name=openapi_url_name), name="redoc"),
    ]
    if extra_urlpatterns is not None:
        docs_urlpatterns.extend(extra_urlpatterns)

    return path(prefix, include(docs_urlpatterns))
