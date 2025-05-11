from rest_framework import serializers 


class BaseMessageSerializer(serializers.Serializer):
    message = serializers.CharField()