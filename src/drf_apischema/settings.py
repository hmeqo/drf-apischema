from dataclasses import dataclass
from typing import TypeVar

from django.conf import settings


@dataclass
class ApiSettings:
    TRANSACTION: bool = True
    """Enable transaction wrapping for APIs"""

    SQL_LOGGING: bool = settings.DEBUG
    """Enable SQL logging"""

    SQL_LOGGING_REINDENT: bool = True
    """Indent SQL queries"""

    SUMMARY_FROM_DOC: bool = True
    """Use method docstring as summary and description"""

    SHOW_PERMISSIONS: bool = True
    """Show permissions in description"""

    ACTION_DEFAULTS_EMPTY: bool = False
    """If True, request_body and response will be empty by default if the view is action decorated"""

    OPENAPI_URL_NAME: str = "openapi.json"
    """OpenAPI URL name"""


api_settings = ApiSettings(**getattr(settings, "DRF_APISCHEMA_SETTINGS", {}))


T = TypeVar("T")


def with_override(default: T, override: T = None) -> T:
    if override is not None:
        return override
    return default
