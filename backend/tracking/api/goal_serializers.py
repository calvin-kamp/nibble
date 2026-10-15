import re
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from tracking.models import WEIGHT_MAX, WEIGHT_MIN, BodyData, DailyGoal

from .weight_serializers import (
    WEIGHT_DECIMALS_MESSAGE,
    WEIGHT_RANGE_MESSAGE,
    MeasurementSerializer,
    weight_field,
)

KCAL_MIN = 1000
KCAL_MAX = 10000
MACRO_MAX = 2000
WORKOUTS_MAX = 20
# Compound option value of the calculator: groupIndex-optionIndex-MET.
WORKOUT_MET = re.compile(r"^\d{1,2}-\d{1,2}-\d{1,2}(\.\d{1,2})?$")


def user_today(value):
    """The client's today; the server runs on UTC and may be a day off."""
    server = timezone.localdate()

    if value is None:
        return server

    if abs(value - server) > timedelta(days=1):
        raise serializers.ValidationError("Das Datum passt nicht zu heute.")

    return value


class WorkoutSerializer(serializers.Serializer):
    met = serializers.RegexField(WORKOUT_MET)
    duration = serializers.IntegerField(min_value=0, max_value=600)
    frequency = serializers.IntegerField(min_value=0, max_value=7)


class BodyDataSerializer(serializers.ModelSerializer):
    """Calculator inputs. Reading gives the age as of today."""

    age = serializers.IntegerField(
        min_value=14, max_value=120, allow_null=True, required=False
    )
    height = serializers.IntegerField(
        min_value=120, max_value=250, allow_null=True, required=False
    )
    steps = serializers.IntegerField(
        min_value=0, max_value=50000, allow_null=True, required=False
    )
    workouts = WorkoutSerializer(many=True, required=False, max_length=WORKOUTS_MAX)

    class Meta:
        model = BodyData
        fields = ("sex", "age", "height", "steps", "workouts", "goal")
        extra_kwargs = {"sex": {"required": False}, "goal": {"required": False}}

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["age"] = instance.current_age(
            self.context.get("today", timezone.localdate())
        )

        return data


class DailyGoalSerializer(serializers.ModelSerializer):
    weight = weight_field(
        required=False,
        allow_null=True,
        min_value=Decimal(WEIGHT_MIN),
        max_value=Decimal(WEIGHT_MAX),
        error_messages={
            "min_value": WEIGHT_RANGE_MESSAGE,
            "max_value": WEIGHT_RANGE_MESSAGE,
            "max_decimal_places": WEIGHT_DECIMALS_MESSAGE,
        },
    )
    kcal = serializers.IntegerField(min_value=KCAL_MIN, max_value=KCAL_MAX)
    protein = serializers.IntegerField(min_value=0, max_value=MACRO_MAX)
    carbs = serializers.IntegerField(min_value=0, max_value=MACRO_MAX)
    fat = serializers.IntegerField(min_value=0, max_value=MACRO_MAX)

    class Meta:
        model = DailyGoal
        fields = (
            "valid_from",
            "source",
            "kcal",
            "protein",
            "carbs",
            "fat",
            "custom_macros",
            "weight",
        )
        read_only_fields = ("valid_from",)

    def validate(self, attrs):
        # A calculated goal always has the calculated macros.
        if attrs.get("custom_macros") and attrs["source"] != DailyGoal.Source.CUSTOM:
            raise serializers.ValidationError(
                {"custom_macros": ["Eigene Makros gibt es nur bei einem eigenen Wert."]}
            )

        return attrs


class GoalSaveSerializer(serializers.Serializer):
    """PUT /goals/: a new goal version from today, optionally with the inputs
    it was calculated from and the weight as today's measurement."""

    goal = DailyGoalSerializer()
    body = BodyDataSerializer(required=False)
    record_weight = serializers.BooleanField(default=False)
    today = serializers.DateField(required=False, allow_null=True, default=None)

    def validate_today(self, value):
        return user_today(value)

    def validate(self, attrs):
        if attrs["record_weight"] and attrs["goal"].get("weight") is None:
            raise serializers.ValidationError(
                {
                    "goal": {
                        "weight": [
                            "Gib dein Gewicht in Kilogramm ein, zum Beispiel 78,4."
                        ]
                    }
                }
            )

        return attrs


class GoalQuerySerializer(serializers.Serializer):
    heute = serializers.DateField(required=False, allow_null=True, default=None)

    def validate_heute(self, value):
        return user_today(value)


class GoalOverviewSerializer(serializers.Serializer):
    current = DailyGoalSerializer(allow_null=True)
    # The goal before today's version, for "Ersetzt dein bisheriges Ziel von …".
    previous = DailyGoalSerializer(allow_null=True)
    # For "Berechneten Wert verwenden" after a custom value.
    last_calculated = DailyGoalSerializer(allow_null=True)
    body = serializers.SerializerMethodField()
    latest_weight = MeasurementSerializer(allow_null=True)
    # Current week's average minus the weight of the calculation, from ±2 kg on.
    weight_change = weight_field(allow_null=True)

    def get_body(self, overview):
        if overview["body"] is None:
            return None

        return BodyDataSerializer(
            overview["body"], context={"today": overview["today"]}
        ).data
