from drf_yasg import openapi
from rest_framework import serializers

field_openapi_map: dict[type, str] = {
    serializers.UUIDField: openapi.TYPE_STRING,
    serializers.IntegerField: openapi.TYPE_INTEGER,
    serializers.CharField: openapi.TYPE_STRING,
    serializers.BooleanField: openapi.TYPE_BOOLEAN,
    serializers.DateTimeField: openapi.TYPE_STRING,
    serializers.ListField: openapi.TYPE_ARRAY,
    serializers.DictField: openapi.TYPE_OBJECT,
}


def serializer_field_to_schema(field: serializers.Field):
    schema_type = field_openapi_map.get(type(field))
    if not schema_type:
        raise Exception(f"Unsupported field type: {type(field)}")
    schema = openapi.Schema(type=schema_type)
    schema.default = field.default
    schema.description = field.help_text
    return schema
