from django.utils import timezone
from rest_framework import serializers

from .exceptions import FUTURE_DATE_NOT_ALLOWED


def not_in_future(value):
    """'Today' is the Berlin date, see TIME_ZONE."""
    if value > timezone.localdate():
        raise serializers.ValidationError(
            "Das Datum darf nicht in der Zukunft liegen.",
            code=FUTURE_DATE_NOT_ALLOWED,
        )
