__all__ = [
    "apischema",
    "HttpError",
    "NoResponse",
    "NumberResponse",
    "StatusResponse",
    "check_exists",
    "get_object_or_422",
    "is_accept_json",
    "swagger_schema",
    "ASRequest",
    "Response422Serializer",
]

from warnings import warn

from .core import (
    HttpError,
    Response422Serializer,
    apischema,
    check_exists,
    get_object_or_422,
    is_accept_json,
    swagger_schema,
)
from .request import ASRequest
from .response import NoResponse, NumberResponse, StatusResponse

warn(
    "drf-apischema.drf_yasg is not recommended, it will be removed in the future. Please use drf-apischema==0.1.17 instead."
)
