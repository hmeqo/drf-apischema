from __future__ import annotations

import copy
import inspect
import traceback
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Sequence

from django.conf import settings
from django.db import connection, models
from django.db import transaction as _transaction
from django.http import Http404
from django.http.request import HttpRequest
from django.http.response import HttpResponseBase
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from .settings import apisettings

Serializer = type[serializers.BaseSerializer] | serializers.BaseSerializer
Field = type[serializers.Field] | serializers.Field
JsonValue = Mapping | Iterable | float | int | bool
ApiMethod = Callable[..., HttpResponseBase | JsonValue | None]
WrappedMethod = Callable[["ProcessEvent"], HttpResponseBase]
SwaggerResponse = openapi.Response | Serializer | Field


@dataclass
class ProcessEvent:
    request: HttpRequest
    view: Callable | None
    args: tuple
    kwargs: dict


class HttpError(Exception):
    def __init__(self, content: dict | str = "", status: int = status.HTTP_400_BAD_REQUEST):
        if isinstance(content, dict):
            self.content = content
        else:
            self.content = {"detail": content}
        self.status = status


def get_object_or_422(qs: type[models.Model] | models.QuerySet, *args, **kwargs) -> models.Model:
    """Get an object from a queryset or raise a 422 error if it doesn't exist."""
    model = qs.model if isinstance(qs, models.QuerySet) else qs
    try:
        if isinstance(qs, models.QuerySet):
            return qs.get(*args, **kwargs)
        return qs.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        raise HttpError(_("Not found."), status=status.HTTP_422_UNPROCESSABLE_ENTITY)


def check_exists(qs: type[models.Model] | models.QuerySet, *args, raise_error=True, **kwargs) -> bool:
    """Check if an object exists in a queryset or raise a 422 error if it doesn't exist."""
    model = qs.model if isinstance(qs, models.QuerySet) else qs
    flag = model.objects.filter(*args, **kwargs).exists()
    if raise_error and not flag:
        raise HttpError(_("Not found."), status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    return flag


def is_accept_json(request: HttpRequest):
    """Check if the request accepts JSON."""
    return request.headers.get("accept", "").split(";")[0] == "application/json"


def apischema(
    *,
    permissions: Iterable[type[BasePermission]] | None = None,
    query: Serializer | None = None,
    body: Serializer | None = None,
    response: SwaggerResponse | None = None,
    responses: dict[int, SwaggerResponse] | None = None,
    description: str | None = None,
    tags: Sequence[str] | None = None,
    transaction: bool | None = None,
    deprecated: bool = False,
) -> Callable[[ApiMethod], Callable[..., HttpResponseBase]]:
    """
    Args:
        permissions (Iterable[type[BasePermission]] | None, optional): Permissions required to access the endpoint.
        query (Serializer | None, optional): Serializer for query parameters.
        body (Serializer | None, optional): Serializer for request body.
        response (SwaggerResponse | None, optional): OpenAPI schema for the response.
        responses (dict[int, SwaggerResponse] | None, optional): OpenAPI schema for the response.
        description (str | None, optional): Description of the endpoint.
        tags (Sequence[str] | None, optional): Tags for the endpoint.
        transaction (bool, optional): Whether to wrap the method in a transaction.
        deprecated (bool, optional): Whether the endpoint is deprecated.

    Returns:
        Callable[[ApiMethod], Callable[..., HttpResponseBase]]: The decorated method.
    """

    def decorator(method: ApiMethod) -> Callable[..., HttpResponseBase]:
        wrapper = _response_processor(method)
        if query or body:
            wrapper = _serializer_processor(wrapper, method, query, body)
        if apisettings.transaction(transaction):
            wrapper = _transaction.atomic(wrapper)
        if settings.DEBUG:
            wrapper = _sql_logger(wrapper)
        if permissions:
            wrapper = _permission_processor(wrapper, permissions)
        wrapper = _excpetion_catcher(wrapper)
        wrapper = swagger_schema(
            summary=method.__doc__,
            description=description or "",
            query=query,
            body=body,
            response=response,
            responses=responses,
            tags=method.__qualname__.split(".")[:1] if tags is None else tags,
            deprecated=deprecated,
        )(wrapper)
        return wrapper

    return decorator


def _sql_logger(method: WrappedMethod):
    def wrapper(event: ProcessEvent):
        from rich import get_console

        console = get_console()
        response = method(event)
        for query in connection.queries:
            console.log("sql: {sql}\ntime: {time}\n".format(**query))
        return response

    wrapper.__name__ = method.__name__
    return wrapper


def _excpetion_catcher(method: WrappedMethod):
    def exception_handler(event: ProcessEvent):
        try:
            response = method(event)
        except Http404 as exc:
            raise exc
        except HttpError as exc:
            return Response(exc.content, status=exc.status)
        except ValidationError as exc:
            return Response({"detail": exc.detail}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as exc:
            traceback.print_exception(exc)
            if is_accept_json(event.request):
                return Response({"detail": _("Server error.")}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            raise exc
        return response

    def default_handler(*args, **kwds):
        if hasattr(args[0], "request"):
            request, view = args[1], args[0]
        else:
            request, view = args[0], None
        event = ProcessEvent(request=request, view=view, args=args, kwargs=kwds)
        return exception_handler(event)

    default_handler.__name__ = method.__name__
    return default_handler


def _response_processor(method: ApiMethod):
    def wrapper(event: ProcessEvent) -> HttpResponseBase:
        response = method(*event.args, **event.kwargs)
        if response is None:
            response = Response(status=status.HTTP_204_NO_CONTENT)
        elif isinstance(response, HttpResponseBase):
            response = response
        else:
            response = Response(response)
        return response

    wrapper.__name__ = method.__name__
    return wrapper


def _serializer_processor(
    method: WrappedMethod,
    o_method: Callable[..., Any],
    query: Serializer | None = None,
    body: Serializer | None = None,
):
    need_serializer = "serializer" in o_method.__annotations__
    need_data = "data" in o_method.__annotations__
    if query:

        def get_serializer(request):
            if isinstance(query, serializers.BaseSerializer):
                serializer = copy.deepcopy(query)
                serializer.initial_data = request.GET
            else:
                serializer = query(data=request.GET)
            return serializer

    elif body:

        def get_serializer(request):
            if isinstance(body, serializers.BaseSerializer):
                serializer = copy.deepcopy(body)
                serializer.initial_data = request.data
            else:
                serializer = body(data=request.data)
            return serializer

    else:
        raise ValueError("query or body is required")

    def wrapper(event: ProcessEvent):
        serializer = get_serializer(event.request)
        serializer.is_valid(raise_exception=True)

        if need_serializer:
            event.kwargs["serializer"] = serializer
        if need_data:
            event.kwargs["data"] = serializer.validated_data
        return method(event)

    wrapper.__name__ = method.__name__
    return wrapper


def _permission_processor(
    method: WrappedMethod,
    permissions: Iterable[type[BasePermission]],
):
    __permissions = [permission() for permission in permissions]

    def wrapper(event: ProcessEvent):
        for permission in __permissions:
            if permission.has_permission(event.request, event.view):
                return method(event)
        raise HttpError(_("You do not have permission to perform this action."), status=status.HTTP_403_FORBIDDEN)

    wrapper.__name__ = method.__name__
    return wrapper


class Response422Serializer(serializers.Serializer):
    detail = serializers.Field()


def swagger_schema(
    query: Serializer | None = None,
    body: Serializer | None = None,
    response: SwaggerResponse | None = None,
    responses: dict[int, SwaggerResponse] | None = None,
    summary: str | None = None,
    description: str | None = None,
    tags: Sequence[str] | None = None,
    deprecated: bool | None = None,
):
    if response is not None and inspect.isclass(response):
        response = response()

    responses = responses or {}
    if response is None:
        responses.setdefault(status.HTTP_204_NO_CONTENT, openapi.Response(""))
    else:
        responses.setdefault(status.HTTP_200_OK, response)
    if query or body:
        responses.setdefault(status.HTTP_422_UNPROCESSABLE_ENTITY, Response422Serializer())
    responses = dict(sorted(responses.items(), key=lambda x: x[0]))

    return swagger_auto_schema(
        query_serializer=query,
        request_body=body,
        responses=responses,
        operation_summary=summary,
        operation_description=description,
        tags=tags,
        deprecated=deprecated,
    )
