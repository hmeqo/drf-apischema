from __future__ import annotations

import functools
import inspect
import sys
import traceback
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Sequence

from django.db import connection
from django.db import transaction as _transaction
from django.http import Http404
from django.http.response import HttpResponseBase
from django.utils.translation import gettext_lazy as _
from drf_spectacular.drainage import get_view_method_names
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework.settings import api_settings as drf_api_settings

from drf_apischema.plumbing import any_success, is_action_view, is_not_empty_none, true_empty_str

from .request import ASRequest
from .response import StatusResponse
from .settings import api_settings, with_override
from .utils import HttpError, is_accept_json


@dataclass
class ProcessEvent:
    request: ASRequest
    view: Callable | None
    args: tuple
    kwargs: dict

    def get_object(self):
        return self.view.get_object() if self.detail else None  # type: ignore

    @property
    def query_data(self):
        return self.request.GET

    @property
    def body_data(self):
        return self.request.data

    @property
    def detail(self) -> bool:
        return self.view.detail if self.view else False


@dataclass
class ArgCollection:
    func: Any
    cls: Any
    permissions: Iterable[type[BasePermission]] | None
    query: Any
    body: Any
    response: Any
    responses: Any
    summary: str | None
    description: str | None
    tags: Sequence[str] | None
    transaction: bool | None
    sqllogging: bool | None
    sqllogging_callback: Callable[[Any], None] | None
    deprecated: bool


def apischema_view(**kwargs):
    def decorator(view):
        available_view_methods = get_view_method_names(view)
        for method_name, method_decorator in kwargs.items():
            if method_name not in available_view_methods:
                continue

            method = method_decorator(getattr(view, method_name), view)
            setattr(view, method_name, method)
        for method_name in set(available_view_methods).difference(kwargs).difference({"options"}):
            method = apischema()(getattr(view, method_name), view)
            setattr(view, method_name, method)
        return view

    return decorator


def apischema(
    permissions: Iterable[type[BasePermission]] | None = None,
    query: Any = None,
    body: Any = empty,
    response: Any = empty,
    responses: Any = empty,
    summary: str | None = None,
    description: str | None = None,
    tags: Sequence[str] | None = None,
    transaction: bool | None = None,
    sqllogging: bool | None = None,
    sqllogging_callback: Callable[[Any], None] | None = None,
    deprecated: bool = False,
    **kwargs,
) -> Callable[..., Callable[..., HttpResponseBase]]:
    """
    :param permissions: The permissions needed to access the endpoint.
    :param query: The serializer used for query parameters.
    :param body: The serializer used for the request body.
    :param response: The OpenAPI schema for the response.
    :param responses: The OpenAPI schemas for various response codes.
    :param summary: A brief summary of the endpoint.
    :param description: A detailed description of the endpoint.
    :param tags: The tags associated with the endpoint.
    :param transaction: Whether to use a transaction for the endpoint.
    :param sqllogging: Whether to log SQL queries for the endpoint.
    :param sqllogging_callback: A callback to log SQL queries for the endpoint.
    :param deprecated: Whether to mark the endpoint as deprecated.
    :param kwargs: Additional keyword arguments to pass to the `extend_schema` decorator.
    """

    def decorator(func, cls=None):
        args = ArgCollection(
            func=func,
            cls=cls,
            permissions=permissions,
            query=query,
            body=body,
            response=response,
            responses=responses,
            summary=summary,
            description=description,
            tags=tags,
            transaction=transaction,
            sqllogging=sqllogging,
            sqllogging_callback=sqllogging_callback,
            deprecated=deprecated,
        )
        _responses = _get_responses(args)
        _summary, _description = _get_summary_and_description(args)

        func = _response_decorator(func, args)
        if query is not None or is_not_empty_none(body):
            func = _request_decorator(func, args)
        if with_override(api_settings.TRANSACTION, transaction):
            func = _transaction.atomic(func)
        if with_override(api_settings.SQL_LOGGING, sqllogging):
            func = _sql_logging_decorator(func, args)
        if permissions:
            func = _permission_decorator(func, args)
        func = _excpetion_catcher(func, args)

        return extend_schema(
            parameters=[args.query] if args.query else None,
            request=(None if is_action_view(args.func) else empty) if args.body is empty else args.body,
            responses=_responses,
            summary=_summary,
            description=_description,
            tags=tags,
            **kwargs,
        )(func)

    return decorator


def _get_responses(e: ArgCollection):
    response = empty
    if e.response is not empty and inspect.isclass(e.response):
        response = e.response()
    responses = {} if e.responses is empty else e.responses
    if response is not empty:
        if isinstance(response, StatusResponse):
            responses.setdefault(response.status_code, response)
        else:
            responses.setdefault(status.HTTP_200_OK, response)
    if api_settings.ACTION_DEFAULTS_EMPTY and not any_success(responses) and is_action_view(e.func):
        responses = {status.HTTP_204_NO_CONTENT: None}
    if responses:
        responses = dict(sorted(responses.items(), key=lambda x: x[0]))
    else:
        responses = empty
    return responses


def _get_summary_and_description(e: ArgCollection):
    summary = description = None
    doc = getattr(e.func, "description", e.func.__doc__)
    if doc is None:
        _summary = None
    else:
        _summary, *docs = doc.strip("\n").splitlines()
        if e.description is None:
            if sys.version_info >= (3, 13):
                if docs:
                    indent_length = min((len(i) - len(i.lstrip(" ")) for i in docs))
                    docs = [i[indent_length:] for i in docs]
            e.description = "\n".join(docs).strip("\n")
    if e.summary is None:
        summary = _summary

    if api_settings.SHOW_PERMISSIONS:
        permissions: list = list(drf_api_settings.DEFAULT_PERMISSION_CLASSES)
        permissions.extend(getattr(e.cls, "permission_classes", []))
        permissions.extend(e.permissions or [])
        permissions = [
            j for j in (i.__name__ if not isinstance(i, str) else i for i in permissions) if j != AllowAny.__name__
        ]
        if permissions:
            description = f"**Permissions:** `{'` `'.join(permissions)}`"
            if e.description:
                description += f"\n\n{e.description}"
    return summary, description or true_empty_str


def _response_decorator(func: Callable, e: ArgCollection):
    @functools.wraps(func)
    def wrapper(event: ProcessEvent) -> HttpResponseBase:
        response = func(*event.args, **event.kwargs)
        if response is None:
            response = Response(status=status.HTTP_204_NO_CONTENT)
        elif isinstance(response, HttpResponseBase):
            response = response
        else:
            response = Response(response)
        return response

    return wrapper


def _request_decorator(func: Callable, e: ArgCollection):
    if e.query is not None:

        def get_serializer(event: ProcessEvent):
            if isinstance(e.query, serializers.BaseSerializer):
                serializer = e.query
                serializer.instance = event.get_object()
                serializer.initial_data = event.query_data
            else:
                serializer = e.query(instance=event.get_object(), data=event.query_data)
            return serializer

    elif is_not_empty_none(e.body):

        def get_serializer(event: ProcessEvent):
            if isinstance(e.body, serializers.BaseSerializer):
                serializer = e.body
                serializer.instance = event.get_object()
                serializer.initial_data = event.body_data
            else:
                serializer = e.body(instance=event.get_object(), data=event.body_data)
            return serializer

    else:
        raise ValueError("query or body is required")

    @functools.wraps(func)
    def wrapper(event: ProcessEvent):
        serializer = get_serializer(event)
        serializer.is_valid(raise_exception=True)

        event.request.serializer = serializer
        event.request.validated_data = serializer.validated_data
        return func(event)

    return wrapper


def _sql_logging_decorator(func: Callable, e: ArgCollection):
    @functools.wraps(func)
    def wrapper(event: ProcessEvent):
        import sqlparse
        from rich import print as rprint
        from rich.padding import Padding

        response = func(event)
        cache = []
        for query in connection.queries:
            if e.sqllogging_callback is not None:
                e.sqllogging_callback(query)
            sql = sqlparse.format(query["sql"], reindent=api_settings.SQL_LOGGING_REINDENT).strip()
            cache.append(f"[SQL] Time: {query['time']}")
            cache.append(Padding(sql, (0, 0, 0, 2)))
        rprint(*cache)
        return response

    return wrapper


def _permission_decorator(func: Callable, e: ArgCollection):
    __permissions = [permission() for permission in (e.permissions or [])]

    @functools.wraps(func)
    def wrapper(event: ProcessEvent):
        for permission in __permissions:
            if permission.has_permission(event.request, event.view):  # type: ignore
                return func(event)
        raise HttpError(_("You do not have permission to perform this action."), status=status.HTTP_403_FORBIDDEN)

    return wrapper


def _excpetion_catcher(func: Callable, e: ArgCollection):
    def handle_exception(event: ProcessEvent):
        try:
            response = func(event)
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

    @functools.wraps(func)
    def default_wrapper(*args, **kwds):
        if hasattr(args[0], "request"):
            request, view = args[1], args[0]
        else:
            request, view = args[0], None
        event = ProcessEvent(request=request, view=view, args=args, kwargs=kwds)
        return handle_exception(event)

    return default_wrapper
