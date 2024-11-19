## What is it

API schema generator and validator for Django REST framework.

## Usage

```python
from django.urls import include, path
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ViewSet

from drf_apischema import apischem
from drf_apischema.utils import api_patha


class AOut(serializers.ListSerializer):
    child = serializers.IntegerField()


class BQuery(serializers.Serializer):
    n = serializers.IntegerField(default=2)


class AViewSet(ViewSet):
    @apischema(response=AOut)
    def list(self, request):
        return [1, 2, 3]


@api_view(["GET"])
@apischema(query=BQuery, transaction=False)
# def b_view(request, serializer: BQuery, data: dict):
def b_view(request, data: dict):
    n: int = data["n"]
    return n * n


router = DefaultRouter()
router.register("a", AViewSet, basename="a")


urlpatterns = [
    api_path(
        "api/",
        [
            path("", include(router.urls)),
            path("b/", b_view),
        ],
    )
]
```

## settings

```python
# settings.py

# wrap method in a transaction
DRF_APISCHEMA_TRANSACTION = True

# log SQL queries in debug mode
DRF_APISCHEMA_SQLLOGGER = True
DRF_APISCHEMA_SQLLOGGER_REINDENT = True
```
