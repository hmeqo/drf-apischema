from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.inspectors import PaginatorInspector, SwaggerAutoSchema
from drf_yasg.utils import no_body
from rest_framework.pagination import BasePagination
from rest_framework.permissions import AllowAny
from rest_framework.settings import api_settings as drf_api_settings
from rest_framework.status import is_success

from .response import NoResponse
from .settings import api_settings


def is_not_restful(view):
    return view.suffix is None
    # return isinstance(view.action_map, str)


def any_success(responses):
    return any(is_success(int(sc)) for sc in responses if sc != "default")


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

        if api_settings.show_permissions():
            permissions = list(drf_api_settings.DEFAULT_PERMISSION_CLASSES)
            permissions.extend(getattr(self.view, "permission_classes", []))
            permissions.extend(self.overrides.get("permissions", []) or [])
            permissions = [
                j for j in (i.__name__ if not isinstance(i, str) else i for i in permissions) if j != AllowAny.__name__
            ]
            if permissions:
                description = f"**Permissions:** `{'` `'.join(permissions)}`\n\n{description}"
        return summary, description

    def get_request_body_parameters(self, consumes):
        if (
            api_settings.action_method_empty()
            and self.overrides.get("request_body") is None
            and is_not_restful(self.view)
        ):
            self.overrides["request_body"] = no_body
        return super().get_request_body_parameters(consumes)

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

        if api_settings.action_method_empty() and not any_success(manual_responses) and is_not_restful(self.view):
            manual_responses = OrderedDict({NoResponse.status_code: NoResponse.response})

        responses = OrderedDict()
        if not any_success(manual_responses):
            responses = self.get_default_responses()

        responses.update((str(sc), resp) for sc, resp in manual_responses.items())
        return responses
