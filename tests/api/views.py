from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from drf_apischema import ASRequest, apischema

from .serializers import SquareOut, SquareQuery, TestOut

# Create your views here.


class TestViewSet(GenericViewSet):
    """Tag here"""

    serializer_class = TestOut
    permission_classes = [IsAuthenticated]

    # Define a view that requires permissions
    @apischema(permissions=[IsAdminUser], extra_tags=["tag1", "tag2"], security=[{"basic": ["123"]}])
    def list(self, request):
        """List all

        Document here
        xxx
        """
        # Note that apischema won't automatically process the response with the
        # declared response serializer, but it will wrap it with
        # rest_framework.response.Response
        # So you don't need to manually wrap it with Response
        return self.get_serializer([1, 2, 3]).data

    @action(methods=["GET"], detail=False)
    @apischema(query=SquareQuery, response=SquareOut, transaction=False)
    def square(self, request: ASRequest[SquareQuery]):
        """The square of a number"""
        # The request.serializer is an instance of SquareQuery that has been validated
        # print(request.serializer)

        # The request.validated_data is the validated data of the serializer
        n: int = request.validated_data["n"]
        return SquareOut({"result": n * n}).data
