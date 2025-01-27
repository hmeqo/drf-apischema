from typing import Any, Generic, TypeVar

from rest_framework import serializers
from rest_framework.request import Request

ST = TypeVar("ST", bound=serializers.BaseSerializer)


class ASRequest(Request, Generic[ST]):
    serializer: ST
    validated_data: Any
