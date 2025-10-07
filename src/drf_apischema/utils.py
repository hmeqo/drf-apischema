from __future__ import annotations

from typing import Any

from django.db import models
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from rest_framework import status as S


class HttpError(Exception):
    def __init__(self, content: dict | str | Any = "", status: int = S.HTTP_400_BAD_REQUEST):
        if isinstance(content, dict):
            self.content = content
        else:
            self.content = {"detail": content}
        self.status = status


class DetailError(HttpError):
    def __init__(self, detail: str | Any = "", status: int = S.HTTP_400_BAD_REQUEST):
        super().__init__({"detail": detail}, status=S.HTTP_400_BAD_REQUEST)


def get_object_or_404(qs: type[models.Model] | models.QuerySet, *args, **kwargs) -> models.Model:
    """Get an object from a queryset or raise a 404 error if it doesn't exist."""
    model = qs.model if isinstance(qs, models.QuerySet) else qs
    try:
        if isinstance(qs, models.QuerySet):
            return qs.get(*args, **kwargs)
        return qs.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        raise HttpError(_("Not found."), status=S.HTTP_404_NOT_FOUND)


def check_exists(qs: type[models.Model] | models.QuerySet, *args, raise_error=True, **kwargs) -> bool:
    """Check if an object exists in a queryset or raise a 404 error if it doesn't exist."""
    model = qs.model if isinstance(qs, models.QuerySet) else qs
    flag = model.objects.filter(*args, **kwargs).exists()
    if raise_error and not flag:
        raise HttpError(_("Not found."), status=S.HTTP_404_NOT_FOUND)
    return flag


def is_accept_json(request: HttpRequest):
    """Check if the request accepts JSON."""
    return request.headers.get("accept", "").split(";")[0] == "application/json"
