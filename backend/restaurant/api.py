from django.core.exceptions import ValidationError


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .serializers import (
    BookingRequestSerializer,
    CancelRequestSerializer,
    BookingResponseSerializer,
)
from .services import ReserveService
from core.serializers import BaseMessageSerializer


@extend_schema(
    request=BookingRequestSerializer,
    responses={201: BookingResponseSerializer, 400: BaseMessageSerializer},
    tags=["Booking"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def book(request):
    serializer = BookingRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        reserve = ReserveService().create_reserve(
            user_id=request.user.id,
            number_of_people=serializer.validated_data["number_of_people"],
            date=serializer.validated_data["date"],
            from_time=serializer.validated_data["from_time"],
            to_time=serializer.validated_data["to_time"],
        )
        return Response(
            {
                "amount": reserve.amount,
                "table_id": reserve.table.id,
                "number_of_seats": reserve.number_of_seats,
            },
            status=status.HTTP_201_CREATED,
        )
    except ValidationError as e:
        return Response({"message": e.message}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=CancelRequestSerializer,
    responses={200: BaseMessageSerializer, 400: BaseMessageSerializer},
    tags=["Booking"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel(request):
    serializer = CancelRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        ReserveService().cancel_reserve(serializer.validated_data["id"])
        return Response({"message": "the reserve has canceled"})
    except ValidationError as e:
        return Response({"message": e.message}, status=status.HTTP_400_BAD_REQUEST)
