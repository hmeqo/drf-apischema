## Introduction

Automatically generate API documentation, validate queries, bodies, and permissions, handle transactions, and log SQL queries.  
This can greatly speed up development and make the code more readable.

## Installation

Install `drf-apischema` from PyPI

```bash
pip install drf-apischema
```

Configure your project `settings.py` like this

```py
INSTALLED_APPS = [
    # ...
    "drf_yasg",
    "rest_framework",
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

views.py

```python
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import GenericViewSet

from drf_apischema import ASRequest, apischema

from .serializers import SquareOut, SquareQuery, TestOut


class TestViewSet(GenericViewSet):
    serializer_class = TestOut

    # Define a view that requires permissions
    @apischema(permissions=[IsAdminUser])
    def list(self, request):
        """List all users

        Document here
        xxx
        """
        # We don't process the response using the declared serializer
        # but instead wrap it with rest_framework.response.Response
        return self.get_serializer([1, 2, 3]).data

    @action(methods=["GET"], detail=False)
    @apischema(query=SquareQuery, response=SquareOut, transaction=False)
    def square(self, request: ASRequest[SquareQuery]):
        """Square a number"""
        # request.serializer is instance of BQuery that is validated
        # print(request.serializer)

        # request.validated_data is serializer.validated_data
        n: int = request.validated_data["n"]
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
    # Auto-generate /api/swagger/ and /api/redoc/ for documentation
    api_path("api/", [path("", include(router.urls))])
]
```

## settings

settings.py

```python
DRF_APISCHEMA_SETTINGS = {
    # wrap method in a transaction
    "TRANSACTION": True,
    # log SQL queries in debug mode
    "SQL_LOGGER": True,
    # indent SQL queries
    "SQL_LOGGER_REINDENT": True,
    # override default swagger auto schema
    "OVERRIDE_SWAGGER_AUTO_SCHEMA": True,
}
```
