# DRF APISchema

Based on `drf-spectacular`, automatically generate API documentation, validate queries, bodies, and permissions, handle transactions, and log SQL queries.  
This can greatly speed up development and make the code more readable.

## Features

- Auto generate API documentation and routes

- Validate queries, bodies, and permissions

- Handle transactions

- Log SQL queries

- Simple to use

```python
@apischema(permissions=[IsAdminUser], body=UserIn, response=UserOut)
def create(self, request: ASRequest[UserIn]):
    """Description"""
    print(request.serializer, request.validated_data)
    return UserOut(request.serializer.save()).data
```

## Installation

Install `drf-apischema` from PyPI

```bash
pip install drf-apischema
```

Configure your project `settings.py` like this

```py
INSTALLED_APPS = [
    # ...
    "rest_framework",
    "drf_spectacular",
    "drf_apischema.scalar,
    # ...
]

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Your Project API",
    "DESCRIPTION": "Your project description",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    'SCHEMA_PATH_PREFIX': '/api-docs',
}
```

## Usage

serializers.py

```python
from django.contrib.auth.models import User
from rest_framework import serializers


class UserOut(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class SquareOut(serializers.Serializer):
    result = serializers.IntegerField()


class SquareQuery(serializers.Serializer):
    n = serializers.IntegerField(default=2)
```

views.py

```python
from django.contrib.auth.models import User
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from drf_apischema import ASRequest, apischema, apischema_view
from drf_apischema.decorator import action

from .serializers import SquareOut, SquareQuery, UserOut

# Create your views here.


@apischema_view(
    retrieve=apischema(summary="Retrieve a user"),
)
class UserViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    """User management"""

    queryset = User.objects.all()
    serializer_class = UserOut
    # permission_classes = [IsAuthenticated]

    # Define a view that requires permissions
    @apischema(permissions=[IsAdminUser])
    def list(self, request):
        """List all users

        Document here
        xxx
        """
        return super().list(request)

    # will auto wrap it with `apischema` in `apischema_view`
    @action(methods=["post"], detail=True)
    def echo(self, request, pk):
        """Echo the request"""
        return self.get_serializer(self.get_object()).data

    @apischema(query=SquareQuery, response=SquareOut)
    @action(methods=["get"], detail=False)
    def square(self, request: ASRequest[SquareQuery]):
        """The square of a number"""
        # The request.serializer is an instance of SquareQuery that has been validated
        # print(request.serializer)

        # The request.validated_data is the validated data of the serializer
        n: int = request.validated_data["n"]

        # Note that apischema won't automatically process the response with the declared response serializer,
        # but it will wrap it with rest_framework.response.Response
        # So you don't need to manually wrap it with Response
        return SquareOut({"result": n * n}).data
```

urls.py

```python
from django.urls import include, path
from drf_apischema.urls import api_docs_path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register("test", TestViewSet, basename="test")


urlpatterns = [
    path("/api", include(router.urls)),
    # Auto-generate /api-docs/xxx, include /api-docs/scalar/
    api_docs_path(),
]
```

## settings

settings.py

```python
DRF_APISCHEMA_SETTINGS = {
    # Enable transaction wrapping for APIs
    "TRANSACTION": True,
    # Enable SQL logging
    "SQL_LOGGING": settings.DEBUG,
    # Indent SQL queries
    "SQL_LOGGING_REINDENT": True,
    # Use method docstring as summary and description
    "SUMMARY_FROM_DOC": True,
    # Show permissions in description
    "SHOW_PERMISSIONS": True,
    # If True, request_body and response will be empty by default if the view is action decorated
    "ACTION_DEFAULTS_EMPTY": False,
    # OpenAPI URL name
    "OPENAPI_URL_NAME" = "openapi.json"
}
```

## drf-yasg version

See branch drf-yasg, it is not longer supported

## Troubleshooting

### Doesn't showed permissions description of `permission_classes`

Wrap the view with `apischema_view`.

```python
@apischema_view()
class XxxViewSet(GenericViewSet):
    permissions_classes = [IsAuthenticated]
```

### TypeError: cannot be assigned to parameter of type "_View@action"

Just annotate the return type to `Any`, as `apischema` will wrap it with `Response`.
Or use `drf_apischema.decorator.action` instead of rest_framework's `action`

```python
@apischema()
@action(methods=["get"], detail=False)
def xxx(self, request) -> Any:
    ...
```
