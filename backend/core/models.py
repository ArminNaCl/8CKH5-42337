from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeModels(models.Model):
    """
    An Abstact Model to be inhrated by other models to inject timestmp to them
    """

    created_at = models.DateTimeField(_("created_at"), auto_now=True)
    update_at = models.DateTimeField(_("update_at"), auto_now_add=True)

    class Meta:
        abstract = True
