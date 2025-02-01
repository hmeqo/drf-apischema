from copy import deepcopy
from typing import Any

from django.conf import settings

DEFAULT_SETTINGS = {
    # Enable transaction wrapping for APIs
    "TRANSACTION": True,
    # Enable SQL logging when in debug mode
    "SQL_LOGGING": True,
    # Indent SQL queries
    "SQL_LOGGING_REINDENT": True,
    # Override the default swagger auto schema
    "OVERRIDE_SWAGGER_AUTO_SCHEMA": True,
    # Show permissions in description
    "SHOW_PERMISSIONS": True,
    # If True, request_body and response will be empty by default if the view is not restful
    "ACTION_METHOD_EMPTY": True,
}


class ApiSettings:
    def __init__(self):
        self.settings = deepcopy(DEFAULT_SETTINGS).update(getattr(settings, "DRF_APISCHEMA_SETTINGS", {}))

    def transaction(self, override: bool | None = None) -> bool:
        if override is not None:
            return override
        return getattr(self.settings, "TRANSACTION", True)

    def sqllogging(self, override: bool | None = None) -> bool:
        if override is not None:
            return override
        return getattr(self.settings, "SQL_LOGGING", True)

    def sqllogging_reindent(self, override: bool | None = None) -> bool:
        if override is not None:
            return override
        return getattr(self.settings, "SQL_LOGGING_REINDENT", True)

    def override_swagger_auto_schema(self, override: bool | None = None) -> bool:
        if override is not None:
            return override
        return getattr(self.settings, "OVERRIDE_SWAGGER_AUTO_SCHEMA", True)

    def show_permissions(self, override: bool | None = None) -> bool:
        if override is not None:
            return override
        return getattr(self.settings, "SHOW_PERMISSIONS", True)

    def action_method_empty(self, override: bool | None = None) -> bool:
        if override is not None:
            return override
        return getattr(self.settings, "ACTION_METHOD_EMPTY", True)


api_settings = ApiSettings()
