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
    # ...
]

STATIC_URL = "static/"

# Ensure you have been defined it
STATIC_ROOT = BASE_DIR / "static"

# STATICFILES_DIRS = []
```

Run `collectstatic`

```bash
python manage.py collectstatic --noinput
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
from typing import Any

from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from drf_apischema import ASRequest, apischema, apischema_view

from .serializers import SquareOut, SquareQuery, UserOut

# Create your views here.


@apischema_view(
    list=apischema(permissions=[IsAdminUser], response=PageNumberPagination),
    square=apischema(query=SquareQuery),
)
class UserViewSet(ModelViewSet):
    """User management"""

    queryset = User.objects.all()
    serializer_class = UserOut
    permission_classes = [IsAuthenticated]

    # Define a view that requires permissions
    def list(self, request):
        """List all

        Document here
        xxx
        """
        return super().list(request)

    @action(methods=["POST"], detail=True)
    def echo(self, request, pk):
        """Echo the request"""
        return self.get_serializer(self.get_object()).data

    @action(methods=["get"], detail=False)
    def square(self, request: ASRequest[SquareQuery]) -> Any:
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
from rest_framework.routers import DefaultRouter

from drf_apischema.urls import api_path

from .views import *

router = DefaultRouter()
router.register("test", TestViewSet, basename="test")


urlpatterns = [
    # Auto-generate /api/schema/, /api/schema/swagger/ and /api/schema/redoc/ for documentation
    api_path("api/", [path("", include(router.urls))])
]
```

## settings

settings.py

```python
DRF_APISCHEMA_SETTINGS = {
    # Enable transaction wrapping for APIs
    "TRANSACTION": True,
    # Enable SQL logging
    "SQL_LOGGING": True,
    # Indent SQL queries
    "SQL_LOGGING_REINDENT": True,
    # Show permissions in description
    "SHOW_PERMISSIONS": True,
    # If True, request_body and response will be empty by default if the view is action decorated
    "ACTION_DEFAULTS_EMPTY": True,
}
```

## drf-yasg version

[0.1.17](/docs/old.md)
