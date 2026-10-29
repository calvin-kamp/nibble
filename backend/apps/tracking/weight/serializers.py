from rest_framework import serializers

from apps.tracking.models import (
    WeightEntry,
)
from config.validators import not_in_future


class WeightEntrySerializer(serializers.ModelSerializer):
    weight_kg = serializers.DecimalField(
        max_digits=4,
        decimal_places=1,
        min_value=20,
        max_value=500,
    )
    measured_on = serializers.DateField(validators=[not_in_future])

    class Meta:
        model = WeightEntry
        fields = ("id", "weight_kg", "measured_on", "recorded_at")
        read_only_fields = ("recorded_at",)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Gib mindestens ein Feld an.")

        return attrs


class WeekSummarySerializer(serializers.Serializer):
    iso_year = serializers.IntegerField()
    iso_week = serializers.IntegerField()
    week_start = serializers.DateField()
    week_end = serializers.DateField()
    average_kg = serializers.DecimalField(max_digits=4, decimal_places=1)
    entries_count = serializers.IntegerField()
    change_kg = serializers.DecimalField(max_digits=4, decimal_places=1, allow_null=True)
    trend = serializers.CharField(allow_null=True)


class PreviousWeekSerializer(serializers.Serializer):
    iso_year = serializers.IntegerField()
    iso_week = serializers.IntegerField()
    average_kg = serializers.DecimalField(max_digits=4, decimal_places=1)


class WeekDetailSerializer(WeekSummarySerializer):
    previous_week = PreviousWeekSerializer(allow_null=True)
    entries = WeightEntrySerializer(many=True)
