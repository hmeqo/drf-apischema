from rest_framework import serializers


class TestOut(serializers.ListSerializer):
    child = serializers.IntegerField()


class SquareOut(serializers.Serializer):
    result = serializers.IntegerField()


class SquareQuery(serializers.Serializer):
    n = serializers.IntegerField(default=2)
