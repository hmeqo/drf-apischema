from copy import deepcopy

from django.conf import settings

DEFAULT_SETTINGS = {
    "TRANSACTION": True,
    "SQL_LOGGER": True,
    "SQL_LOGGER_REINDENT": True,
    "OVERRIDE_SWAGGER_AUTO_SCHEMA": True,
}


class ApiSettings:
    def __init__(self):
        self.settings = deepcopy(DEFAULT_SETTINGS).update(getattr(settings, "DRF_APISCHEMA_SETTINGS", {}))

    def transaction(self, override: bool | None = None) -> bool:
        if override is not None:
            return override
        return getattr(self.settings, "TRANSACTION", True)

    def sqllogger(self, override: bool | None = None) -> bool:
        if override is not None:
            return override
        return getattr(self.settings, "SQL_LOGGER", True)

    def sqllogger_reindent(self, override: bool | None = None) -> bool:
        if override is not None:
            return override
        return getattr(self.settings, "SQL_LOGGER_REINDENT", True)

    def override_swagger_auto_schema(self, override: bool | None = None) -> bool:
        if override is not None:
            return override
        return getattr(self.settings, "OVERRIDE_SWAGGER_AUTO_SCHEMA", True)


apisettings = ApiSettings()
