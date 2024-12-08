from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.inspectors import PaginatorInspector, SwaggerAutoSchema
from rest_framework.pagination import BasePagination
from rest_framework.status import is_success


class AutoPaginatorInspector(PaginatorInspector):
    def get_paginated_response(self, paginator: BasePagination, response_schema: openapi.Schema):
        return openapi.Schema(**paginator.get_paginated_response_schema(response_schema))


class AutoSchema(SwaggerAutoSchema):
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
