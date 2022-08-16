from decimal import Decimal

from django.db import models


class CurrencyField(models.DecimalField):
    def __init__(self, **kwargs):
        kwargs["max_digits"] = 10
        kwargs["decimal_places"] = 2
        super(CurrencyField, self). __init__(
            **kwargs
        )

    def to_python(self, value):
        try:
            return super(CurrencyField, self).to_python(value).quantize(Decimal("0.01"))
        except AttributeError:
            return None
