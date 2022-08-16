from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel
from geo_city.models import Address


class Partner(TimestampedModel):
    name = models.CharField(_('company name'), db_index=True, max_length=150, null=True, blank=True)
    short_name = models.CharField(_('company short name'), max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=18, db_index=True, null=True, blank=True)
    email = models.EmailField(null=True, db_index=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
