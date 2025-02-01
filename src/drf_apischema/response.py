from copy import copy
from typing import Any

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse
from rest_framework import status


class StatusResponse(OpenApiResponse):
    status_code = status.HTTP_200_OK

    def with_status_code(self, status_code: int) -> Any:
        instance = copy(self)
        instance.status_code = status_code
        return instance


NumberResponse = StatusResponse(OpenApiTypes.INT)
