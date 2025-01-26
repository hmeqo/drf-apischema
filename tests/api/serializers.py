from django.contrib.auth.models import User
from rest_framework import serializers


class UserOut(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class SquareOut(serializers.Serializer):
    result = serializers.IntegerField()


class SquareQuery(serializers.Serializer):
    n = serializers.IntegerField(default=2)
