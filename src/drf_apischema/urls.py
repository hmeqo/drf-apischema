from __future__ import annotations

from django.urls import URLPattern, URLResolver, include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from .scalar.views import scalar_viewer
from .settings import api_settings


def api_path(
    urlpatterns: list[URLResolver | URLPattern],
    prefix: str = "",
    api_prefix: str = "api/",
    docs_prefix: str = "api-docs/",
):
    openapi_url_name = api_settings.OPENAPI_URL_NAME

    docs_urlpatterns = [
        path(f"{openapi_url_name}/", SpectacularAPIView.as_view(), name=openapi_url_name),
        path("scalar/", scalar_viewer, name="scalar", kwargs={"url_name": openapi_url_name}),
        path(
            "swagger-ui/",
            SpectacularSwaggerView.as_view(url_name=openapi_url_name),
            name="swagger-ui",
        ),
        path("redoc/", SpectacularRedocView.as_view(url_name=openapi_url_name), name="redoc"),
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
