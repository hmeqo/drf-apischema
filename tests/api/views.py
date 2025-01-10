from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import GenericViewSet

from drf_apischema import ASRequest, apischema

from .serializers import SquareOut, SquareQuery, TestOut

# Create your views here.


class TestViewSet(GenericViewSet):
    serializer_class = TestOut

    # Define a view that requires permissions
    @apischema(permissions=[IsAdminUser])
    def list(self, request):
        """List all users

        Document here
        xxx
        """
        # We don't process the response using the declared serializer
        # but instead wrap it with rest_framework.response.Response
        return self.get_serializer([1, 2, 3]).data

    @action(methods=["GET"], detail=False)
    @apischema(query=SquareQuery, response=SquareOut, transaction=False)
    def square(self, request: ASRequest[SquareQuery]):
        """Square a number"""
        # request.serializer is instance of BQuery that is validated
        # print(request.serializer)

        # request.validated_data is serializer.validated_data
        n: int = request.validated_data["n"]
        return SquareOut({"result": n * n}).data
