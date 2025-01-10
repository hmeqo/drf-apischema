__all__ = [
    "StatusResponse",
    "NoResponse",
]

from drf_yasg import openapi
from rest_framework import status


class StatusResponse:
    status_code = status.HTTP_200_OK
    response = openapi.Response("")

    def __init__(self, response: openapi.Response | None = None, status_code: int | None = None):
        if response is not None:
            self.response = response
        if status_code is not None:
            self.status_code = status_code

    def __call__(self, description: str | None = None, status_code: int | None = None):
        return self.__class__(
            response=openapi.Response(
                description=self.response.description if description is None else description,
                schema=self.response.schema,
                examples=self.response.examples,
                type=self.response.type,
            ),
            status_code=status_code,
        )


NoResponse = StatusResponse(status_code=status.HTTP_204_NO_CONTENT)

NumberResponse = StatusResponse(openapi.Response("Number", type=openapi.TYPE_INTEGER))
