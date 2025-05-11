from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django.db.models import Case, When, F, Sum, Value
from django.db.models.functions import Coalesce
from django.conf import settings


from core.models import TimeModels


class TableManager(models.Manager):
    """
    by overwriting this Manager we can access to actual capacity
    of each table based on record in reserve Table right now
    """

    def get_queryset(self):
        now = datetime.now()

        return (
            super()
            .get_queryset()
            .annotate(
                reserved_people=Sum(
                    Case(
                        When(
                            reserves__date=now.date(),
                            reserves__status__in=[
                                Reserve.Status.BOOKED,
                                Reserve.Status.PENDING,
                            ],
                            reserves__from_time__lt=now.time(),
                            reserves__to_time__gt=now.time(),
                            then=F("reserves__number_of_seats"),
                        ),
                        default=Value(0),
                        output_field=models.PositiveSmallIntegerField(),
                    )
                ),
                available_capacity=Coalesce(
                    F("capacity") - F("reserved_people"),
                    F("capacity"),
                    output_field=models.PositiveSmallIntegerField(),
                ),
            )
        )


class Table(TimeModels):
    capacity = models.PositiveSmallIntegerField(_("capacity"))
    price = models.DecimalField(
        _("price"), help_text=_("price per seat"), max_digits=9, decimal_places=2
    )

    class Meta:
        verbose_name = _("table")
        verbose_name_plural = _("tables")

    available = TableManager()
    objects = models.Manager()


class Reserve(TimeModels):
    class Status(models.TextChoices):
        PENDING = "pending", _("pending")
        BOOKED = "booked", _("booked")
        CANCELED = "canceled", _("canceled")

    date = models.DateField(_("date"))
    from_time = models.TimeField()
    to_time = models.TimeField()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reserves"
    )
    number_of_people = models.PositiveSmallIntegerField(_("number_of_people"))
    number_of_seats = models.PositiveSmallIntegerField(_("number_of_seats"))

    table = models.ForeignKey(
        "restaurant.Table",
        verbose_name=_("table"),
        related_name="reserves",
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(_("amount"), max_digits=10, decimal_places=2)

    status = models.CharField(
        _("status"), choices=Status.choices, default=Status.PENDING
    )

    class Meta:
        verbose_name = _("reserve")
        verbose_name_plural = _("reserves")
