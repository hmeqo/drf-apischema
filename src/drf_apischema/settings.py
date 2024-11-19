from django.conf import settings


class ApiSettings:
    def transaction(self, override: bool | None = None) -> bool:
        if override is not None:
            return override
        return getattr(settings, "DRF_APISPEC_TRANSACTION", True)

    def sqllogger(self, override: bool | None = None) -> bool:
        if override is not None:
            return override
        return getattr(settings, "DRF_APISPEC_SQLLOGGER", True)


apisettings = ApiSettings()
