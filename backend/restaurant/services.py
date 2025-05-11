from django.db.models import F

from .models import Table, Reserve
from django.db.models import Case, When, F, Sum, Value, PositiveSmallIntegerField, Q
from django.db.models.functions import Coalesce

from django.core.exceptions import ValidationError


class ReserveService:

    def get_object(self, reserve_id: int) -> Reserve:
        try:
            return Reserve.objects.get(id=reserve_id)
        except Reserve.DoesNotExist:
            raise ValidationError("Reserve not found.")

    def _return_table(
        self, number_of_people: int, date, from_time, to_time
    ) -> Table | None:
        queryset = Table.objects.annotate(
            reserved_people=Sum(
                Case(
                    When(
                        Q(
                            reserves__date=date,
                            reserves__status__in=[
                                Reserve.Status.BOOKED,
                                Reserve.Status.PENDING,
                            ],
                        )
                        & Q(
                            Q(
                                reserves__from_time__lte=from_time,
                                reserves__to_time__gte=from_time,
                            )
                            | Q(
                                reserves__from_time__lte=to_time,
                                reserves__to_time__gte=to_time,
                            )
                        ),
                        then=F("reserves__number_of_seats"),
                    ),
                    default=Value(0),
                    output_field=PositiveSmallIntegerField(),
                )
            ),
            available_capacity=Coalesce(
                F("capacity") - F("reserved_people"),
                F("capacity"),
                output_field=PositiveSmallIntegerField(),
            ),
        )
        if number_of_people % 2:
            return (
                queryset.filter(
                    available_capacity=F("capacity"),
                    available_capacity__gte=number_of_people,
                )
                .order_by("price")
                .first()
            )
        else:
            return (
                queryset.filter(available_capacity__gte=number_of_people)
                .order_by("price")
                .first()
            )

    def create_reserve(
        self, user_id: int, number_of_people: int, date, from_time, to_time
    ) -> Reserve:

        table = self._return_table(number_of_people, date, from_time, to_time)
        if not table:
            raise ValidationError("No Table is Available Right Now")

        if number_of_people % 2:
            number_of_seats = table.capacity
            amount = table.price * (table.capacity - 1)
        else:
            number_of_seats = number_of_people
            amount = number_of_people * table.capacity

        return Reserve.objects.create(
            table_id=table.id,
            user_id=user_id,
            number_of_people=number_of_people,
            number_of_seats=number_of_seats,
            date=date,
            from_time=from_time,
            to_time=to_time,
            amount=amount,
        )

    def create_payment_gateway(self):
        return "FAKE PAYMENT GATEWAY"

    def validate_payment_call_back(self, reserve_id: int) -> None:
        reserve = self.get_object(reserve_id)
        reserve.status = Reserve.Status.BOOKED
        reserve.save()

    def cancel_reserve(self, reserve_id: int, user_id: int):
        reserve = self.get_object(reserve_id)
        if reserve.user_id != user_id:
            raise ValidationError("You are not allowed to cancel this Reserve.")
        reserve.status = Reserve.Status.CANCELED
        reserve.save()
