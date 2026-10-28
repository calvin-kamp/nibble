from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from config.fields import RoundedDecimalField
from config.serializers import MacrosSerializer
from config.validators import not_in_future
from foods.api.serializers import BARCODE_PATTERN, NutritionPer100Serializer
from foods.models import FoodProduct
from tracking.models import (
    BodyProfile,
    FoodUnit,
    Goal,
    GoalSetting,
    Meal,
    MealItem,
    MealType,
    TrackingEntry,
    WeightEntry,
)
from tracking.utils.nutrition import MACROS, check_unit, scaled_values, snapshot_of

# Nibble is for people aged 16 and up (privacy policy, section 20)
MIN_AGE = 16


class AmountField(RoundedDecimalField):
    def __init__(self, **kwargs):
        super().__init__(
            decimal_places=2,
            min_value=Decimal("0.01"),
            max_value=100000,
            **kwargs,
        )


def per_100_or_none(snapshot):
    if snapshot.kcal_per_100 is None:
        return None

    return NutritionPer100Serializer(snapshot).data


def product_for(off_code):
    product = FoodProduct.objects.filter(code=off_code).first()

    if product is None:
        raise serializers.ValidationError(
            {"off_code": "Dieses Lebensmittel gibt es nicht im Bestand."}
        )

    return product


# ------------------------------------------------------------------------------
# Goal
# ------------------------------------------------------------------------------


class TargetsSerializer(serializers.Serializer):
    kcal = RoundedDecimalField(decimal_places=1, min_value=500, max_value=10000)
    protein = RoundedDecimalField(decimal_places=1, min_value=0, max_value=1000)
    carbs = RoundedDecimalField(decimal_places=1, min_value=0, max_value=2000)
    fat = RoundedDecimalField(decimal_places=1, min_value=0, max_value=1000)


class GoalStateSerializer(serializers.ModelSerializer):
    targets = serializers.SerializerMethodField()

    class Meta:
        model = GoalSetting
        fields = ("goal", "targets", "valid_from")

    def get_targets(self, setting):
        return TargetsSerializer(setting).data if setting.has_targets else None


EMPTY_GOAL_STATE = {"goal": None, "targets": None, "valid_from": None}


class GoalUpdateSerializer(serializers.Serializer):
    goal = serializers.ChoiceField(choices=Goal, required=False)
    targets = TargetsSerializer(required=False)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Gib ein Ziel oder Zielwerte an.")

        return attrs


# ------------------------------------------------------------------------------
# Entries
# ------------------------------------------------------------------------------


class TrackingEntrySerializer(serializers.ModelSerializer):
    nutrition_per_100 = serializers.SerializerMethodField()

    class Meta:
        model = TrackingEntry
        fields = (
            "id",
            *MACROS,
            "source",
            "food_name",
            "brand",
            "off_code",
            "nutrition_per_100",
            "serving_quantity",
            "amount",
            "unit",
            "consumed_on",
            "meal_type",
            "tracked_at",
        )

    def get_nutrition_per_100(self, entry):
        return per_100_or_none(entry)


class EntryInputSerializer(serializers.Serializer):
    off_code = serializers.RegexField(BARCODE_PATTERN)
    amount = AmountField()
    unit = serializers.ChoiceField(choices=FoodUnit)
    consumed_on = serializers.DateField(validators=[not_in_future])
    meal_type = serializers.ChoiceField(choices=MealType)

    def validate(self, attrs):
        product = product_for(attrs["off_code"])
        check_unit(attrs["unit"], product.base_unit, product.serving_quantity)

        return {
            "consumed_on": attrs["consumed_on"],
            "meal_type": attrs["meal_type"],
            **snapshot_of(product, attrs["amount"], attrs["unit"]),
        }


class EntryFromMealSerializer(serializers.Serializer):
    meal_id = serializers.IntegerField()
    consumed_on = serializers.DateField(validators=[not_in_future])
    meal_type = serializers.ChoiceField(choices=MealType)


class EntryPatchSerializer(serializers.Serializer):
    amount = AmountField(required=False)
    unit = serializers.ChoiceField(choices=FoodUnit, required=False)
    consumed_on = serializers.DateField(required=False, validators=[not_in_future])
    meal_type = serializers.ChoiceField(choices=MealType, required=False)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Gib mindestens ein Feld an.")

        entry = self.instance
        changes_amount = "amount" in attrs or "unit" in attrs

        if entry.source == TrackingEntry.Source.MEAL and changes_amount:
            raise serializers.ValidationError(
                {
                    field: "Bei Mahlzeiten lassen sich nur Datum und Mahlzeit ändern."
                    for field in ("amount", "unit")
                    if field in attrs
                }
            )

        if changes_amount:
            unit = attrs.get("unit", entry.unit)
            check_unit(unit, entry.base_unit, entry.serving_quantity)

            # Recalculated from the values stored in the entry, not from OFF.
            snapshot = {
                **{f"{key}_per_100": getattr(entry, f"{key}_per_100") for key in MACROS},
                "serving_quantity": entry.serving_quantity,
                "amount": attrs.get("amount", entry.amount),
                "unit": unit,
            }
            attrs.update(scaled_values(snapshot))

        return attrs

    def update(self, entry, validated_data):
        for field, value in validated_data.items():
            setattr(entry, field, value)

        entry.save()

        return entry


# ------------------------------------------------------------------------------
# Meals
# ------------------------------------------------------------------------------


class MealItemInputSerializer(serializers.Serializer):
    off_code = serializers.RegexField(BARCODE_PATTERN)
    amount = AmountField()
    unit = serializers.ChoiceField(choices=FoodUnit)

    def validate(self, attrs):
        product = product_for(attrs["off_code"])
        check_unit(attrs["unit"], product.base_unit, product.serving_quantity)

        return snapshot_of(product, attrs["amount"], attrs["unit"])


class MealInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    note = serializers.CharField(max_length=300, required=False, allow_blank=True)
    items = MealItemInputSerializer(many=True, min_length=1, max_length=50)


class MealItemSerializer(serializers.ModelSerializer):
    nutrition_per_100 = NutritionPer100Serializer(source="*", read_only=True)

    class Meta:
        model = MealItem
        fields = (
            *MACROS,
            "off_code",
            "food_name",
            "brand",
            "amount",
            "unit",
            "nutrition_per_100",
            "serving_quantity",
        )


class MealSerializer(serializers.ModelSerializer):
    items = MealItemSerializer(many=True, read_only=True)
    totals = MacrosSerializer(source="*", read_only=True)

    class Meta:
        model = Meal
        fields = ("id", "name", "note", "items", "totals")


# ------------------------------------------------------------------------------
# Body
# ------------------------------------------------------------------------------


def age_on(birth_date, day):
    had_birthday = (day.month, day.day) >= (birth_date.month, birth_date.day)

    return day.year - birth_date.year - (0 if had_birthday else 1)


class BodyProfileSerializer(serializers.ModelSerializer):
    """Same limits as the calorie calculator, otherwise it couldn't use the values."""

    birth_date = serializers.DateField(allow_null=True, required=False)
    height_cm = serializers.IntegerField(
        min_value=120,
        max_value=250,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = BodyProfile
        fields = ("birth_date", "height_cm", "sex")
        extra_kwargs = {"sex": {"allow_null": True, "required": False}}

    def validate_birth_date(self, value):
        if value is None:
            return value

        age = age_on(value, timezone.localdate())

        if age < 0:
            raise serializers.ValidationError("Das Datum liegt in der Zukunft.")

        if age < MIN_AGE:
            raise serializers.ValidationError(
                f"Du musst mindestens {MIN_AGE} Jahre alt sein."
            )

        if age > 120:
            raise serializers.ValidationError("Prüf das Datum noch mal.")

        return value


EMPTY_BODY_PROFILE = {"birth_date": None, "height_cm": None, "sex": None}


# ------------------------------------------------------------------------------
# Weight
# ------------------------------------------------------------------------------


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
