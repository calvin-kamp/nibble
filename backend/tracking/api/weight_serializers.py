from decimal import Decimal

from rest_framework import serializers

from tracking.models import WEIGHT_MAX, WEIGHT_MIN, WeightEntry
from tracking.weight import PERIODS

WEIGHT_EMPTY_MESSAGE = "Gib dein Gewicht in Kilogramm ein, zum Beispiel 78,4."
WEIGHT_DECIMALS_MESSAGE = "Gib das Gewicht mit höchstens einer Nachkommastelle ein."
WEIGHT_RANGE_MESSAGE = (
    f"Das Gewicht muss zwischen {WEIGHT_MIN} und {WEIGHT_MAX} kg liegen."
)


def weight_field(**kwargs):
    return serializers.DecimalField(
        max_digits=4, decimal_places=1, coerce_to_string=False, **kwargs
    )


class MeasurementSerializer(serializers.ModelSerializer):
    weight = weight_field(read_only=True)

    class Meta:
        model = WeightEntry
        fields = ("date", "weight")


class WeightInputSerializer(serializers.Serializer):
    weight = weight_field(
        min_value=Decimal(WEIGHT_MIN),
        max_value=Decimal(WEIGHT_MAX),
        error_messages={
            "required": WEIGHT_EMPTY_MESSAGE,
            "null": WEIGHT_EMPTY_MESSAGE,
            "invalid": WEIGHT_EMPTY_MESSAGE,
            "min_value": WEIGHT_RANGE_MESSAGE,
            "max_value": WEIGHT_RANGE_MESSAGE,
            "max_decimal_places": WEIGHT_DECIMALS_MESSAGE,
            "max_digits": WEIGHT_RANGE_MESSAGE,
        },
    )


class WeightQuerySerializer(serializers.Serializer):
    zeitraum = serializers.ChoiceField(choices=list(PERIODS), default="30")
    # The user's today; the server runs on UTC and may already be a day ahead.
    bis = serializers.DateField(required=False)


class WeekSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    week = serializers.IntegerField()
    start = serializers.DateField()
    end = serializers.DateField()
    average = weight_field()
    change = weight_field(allow_null=True)
    is_current = serializers.BooleanField()
    measurements = MeasurementSerializer(many=True)


class StatsSerializer(serializers.Serializer):
    start = weight_field()
    current = weight_field()
    change = weight_field()
    per_week = weight_field(allow_null=True)
    count = serializers.IntegerField()


class WeightOverviewSerializer(serializers.Serializer):
    period = serializers.CharField()
    start = serializers.DateField(allow_null=True)
    end = serializers.DateField()
    latest = MeasurementSerializer(allow_null=True)
    measurements = MeasurementSerializer(many=True)
    weeks = WeekSerializer(many=True)
    stats = StatsSerializer(allow_null=True)
