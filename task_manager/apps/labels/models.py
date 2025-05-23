from django.db import models
from django.utils.translation import gettext_lazy as _


class Label(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Name"))
    date_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Date of creation")
    )

    def __str__(self):
        return self.name
