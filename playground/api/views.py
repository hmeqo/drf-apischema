from typing import Any

from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from drf_apischema import ASRequest, apischema, apischema_view

from .serializers import SquareOut, SquareQuery, UserOut

# Create your views here.


@apischema_view(
    retrieve=apischema(summary="Retrieve a user"),
)
class UserViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    """User management"""

    queryset = User.objects.all()
    serializer_class = UserOut
    # permission_classes = [IsAuthenticated]

    # Define a view that requires permissions
    @apischema(permissions=[IsAdminUser])
    def list(self, request):
        """List all users

        Document here
        xxx
        """
        return super().list(request)

    # will auto wrap it with `apischema` in `apischema_view`
    @action(methods=["post"], detail=True)
    def echo(self, request, pk):
        """Echo the request"""
        return self.get_serializer(self.get_object()).data

    @apischema(query=SquareQuery, response=SquareOut)
    @action(methods=["get"], detail=False)
    def square(self, request: ASRequest[SquareQuery]) -> Any:
        """The square of a number"""
        # The request.serializer is an instance of SquareQuery that has been validated
        # print(request.serializer)

        # The request.validated_data is the validated data of the serializer
        n: int = request.validated_data["n"]

        # Note that apischema won't automatically process the response with the declared response serializer,
        # but it will wrap it with rest_framework.response.Response
        # So you don't need to manually wrap it with Response
        return SquareOut({"result": n * n}).data
