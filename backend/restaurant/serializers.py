from rest_framework import serializers

from .models import Reserve


class BookingRequestSerializer(serializers.Serializer):
    number_of_people = serializers.IntegerField(min_value=1)
    date = serializers.DateField()
    from_time = serializers.TimeField()
    to_time = serializers.TimeField()
    

class BookingResponseSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=9, decimal_places=2)
    table_id = serializers.IntegerField()
    number_of_seats = serializers.IntegerField()
    

class CancelRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
