from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin

from drf_apischema import ASRequest, apischema

from .serializers import SquareOut, SquareQuery, UserOut

# Create your views here.


class UserViewSet(GenericViewSet, ListModelMixin):
    """User management"""

    queryset = User.objects.all()
    serializer_class = UserOut
    permission_classes = [IsAuthenticated]

    # Define a view that requires permissions
    @apischema(permissions=[IsAdminUser], extra_tags=["tag1", "user"])
    def list(self, request):
        """List all

        Document here
        xxx
        """
        return super().list(request)

    @action(methods=["GET"], detail=False)
    @apischema(query=SquareQuery, response=SquareOut, transaction=False)
    def square(self, request: ASRequest[SquareQuery]):
        """The square of a number"""
        # The request.serializer is an instance of SquareQuery that has been validated
        # print(request.serializer)

        # The request.validated_data is the validated data of the serializer
        n: int = request.validated_data["n"]

        # Note that apischema won't automatically process the response with the declared response serializer,
        # but it will wrap it with rest_framework.response.Response
        # So you don't need to manually wrap it with Response
        return SquareOut({"result": n * n}).data

    @action(methods=["POST"], detail=True)
    @apischema(response=UserOut)
    def echo(self, request, pk):
        """Echo the request"""
        return self.get_serializer(self.get_object()).data
