from django.conf import settings


class ApiSettings:
    def transaction(self, override: bool | None) -> bool:
        if override is not None:
            return override
        return getattr(settings, "DRF_APISPEC_TRANSACTION", True)


apisettings = ApiSettings()
