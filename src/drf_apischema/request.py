__all__ = [
    "ASRequest",
]

from typing import Any, Generic, TypeVar

from rest_framework import serializers
from rest_framework.request import Request

ST = TypeVar("ST", bound=serializers.BaseSerializer)


class ASRequest(Generic[ST], Request):
    serializer: ST
    validated_data: Any
