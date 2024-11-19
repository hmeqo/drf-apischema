from django.conf import settings


class ApiSettings:
    def transaction(self, override: bool | None = None) -> bool:
        if override is not None:
            return override
        return getattr(settings, "DRF_APISCHEMA_TRANSACTION", True)

    def sqllogger(self, override: bool | None = None) -> bool:
        if override is not None:
            return override
        return getattr(settings, "DRF_APISCHEMA_SQLLOGGER", True)

    def sqllogger_reindent(self, override: bool | None = None) -> bool:
        if override is not None:
            return override
        return getattr(settings, "DRF_APISCHEMA_SQLLOGGER_REINDENT", True)


apisettings = ApiSettings()
