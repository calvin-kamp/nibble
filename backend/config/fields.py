from decimal import ROUND_HALF_UP

from rest_framework import serializers


class RoundedDecimalField(serializers.DecimalField):
    """Decimal that rounds extra places half up instead of rejecting them."""

    def __init__(self, **kwargs):
        kwargs.setdefault("max_digits", 12)
        kwargs.setdefault("rounding", ROUND_HALF_UP)
        super().__init__(**kwargs)

    def validate_precision(self, value):
        # Only the range matters here, quantize() takes care of the places.
        if self.max_value is not None and value > self.max_value:
            self.fail("max_value", max_value=self.max_value)

        if self.min_value is not None and value < self.min_value:
            self.fail("min_value", min_value=self.min_value)

        return value
