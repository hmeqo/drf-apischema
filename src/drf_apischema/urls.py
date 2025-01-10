from typing import Any

from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import BasePermission, IsAdminUser


def doc_path(urls: Any, title="API", version="v1", pattern_prefix="", permissions: list[BasePermission] | None = None):
    schema_view = get_schema_view(
        openapi.Info(
            title=title,
            default_version=version,
            # description='',
            # terms_of_service='https://www.google.com/policies/terms/',
            # contact=openapi.Contact(email='contact@snippets.local'),
            # license=openapi.License(name='BSD License'),
        ),
        public=False,
        permission_classes=permissions or [IsAdminUser],
        patterns=[re_path(pattern_prefix, include(urls))],
    )

    return list_path(
        pattern_prefix,
        [
            re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
            re_path(r"^swagger/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
            re_path(r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
        ],
    )


def _urls_module_like(urls: Any):
    if hasattr(urls, "urlpatterns"):
        return urls

    class Urls:
        urlpatterns = urls

    return Urls


def list_path(preffix: str, urlpatterns: Any):
    return path(preffix, include(_urls_module_like(urlpatterns)))


def api_path(pattern_prefix: str, urlpatterns: Any, version="", permissions: list[BasePermission] | None = None):
    urls = _urls_module_like(urlpatterns)
    return list_path(
        "",
        [
            doc_path(urls, pattern_prefix=pattern_prefix, version=version, permissions=permissions),
            re_path(pattern_prefix, include(urls)),
        ],
    )
