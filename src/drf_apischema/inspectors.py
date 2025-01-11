from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.inspectors import PaginatorInspector, SwaggerAutoSchema
from rest_framework.pagination import BasePagination
from rest_framework.permissions import AllowAny
from rest_framework.settings import api_settings
from rest_framework.status import is_success

from .settings import apisettings


class AutoPaginatorInspector(PaginatorInspector):
    def get_paginated_response(self, paginator: BasePagination, response_schema: openapi.Schema):
        return openapi.Schema(**paginator.get_paginated_response_schema(response_schema))


class AutoSchema(SwaggerAutoSchema):
    def get_tags(self, operation_keys=None):
        tags = super().get_tags(operation_keys)

        if not self.overrides.get("tags"):
            class_doc = self.view.__class__.__doc__
            if class_doc:
                tags[0] = f"{tags[0]} - {class_doc.split('\n',)[0]}"

        tags.extend(self.overrides.get("extra_tags", []) or [])
        return tags

    def get_summary_and_description(self):
        summary, description = super().get_summary_and_description()

        if apisettings.show_permissions():
            permissions = [i for i in api_settings.DEFAULT_PERMISSION_CLASSES if i is not AllowAny]
            permissions.extend([i.__name__ for i in getattr(self.view, "permission_classes", [])])
            permissions.extend([i.__name__ for i in self.overrides.get("permissions", []) or []])
            if permissions:
                description = f"**Permissions:** `{'` `'.join(permissions)}`\n\n{description}"

        return summary, description

    def get_response_serializers(self):
        manual_responses = self.overrides.get("responses", None) or {}
        manual_responses = OrderedDict((str(sc), resp) for sc, resp in manual_responses.items())

        if self.overrides["pagination_class"] is not None:

            class Override:
                def get_serialzier(self):
                    return serializer

            self.view.paginator = self.overrides["pagination_class"]()
            serializer = manual_responses.pop("200")
            self.view.get_serializer = Override().get_serialzier

        responses = OrderedDict()
        if not any(is_success(int(sc)) for sc in manual_responses if sc != "default"):
            responses = self.get_default_responses()

        responses.update((str(sc), resp) for sc, resp in manual_responses.items())
        return responses
