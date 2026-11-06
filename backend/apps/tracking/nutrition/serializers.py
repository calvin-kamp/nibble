from decimal import Decimal

from rest_framework import serializers

from apps.foods.models import FoodProduct
from apps.foods.search.serializers import NutritionPer100Serializer
from apps.foods.utils import PRODUCT_CODE_PATTERN
from apps.tracking.models import (
    FoodUnit,
    Goal,
    GoalSetting,
    Meal,
    MealItem,
    MealType,
    TrackingEntry,
)
from apps.tracking.nutrition.utils import (
    MACROS,
    check_unit,
    kcal_from_macros,
    manual_snapshot,
    scaled_values,
    snapshot_of,
)
from config.fields import RoundedDecimalField
from config.serializers import MacrosSerializer
from config.validators import not_in_future


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
    off_code = serializers.RegexField(PRODUCT_CODE_PATTERN)
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


# Values of one portion, so above the limits per 100 g of the moderation form.
MAX_MANUAL_KCAL = 10000
MAX_MANUAL_GRAMS = 1000


def manual_grams(**kwargs):
    return RoundedDecimalField(
        decimal_places=1, min_value=0, max_value=MAX_MANUAL_GRAMS, **kwargs
    )


def manual_kcal(**kwargs):
    return RoundedDecimalField(
        decimal_places=1,
        min_value=0,
        max_value=MAX_MANUAL_KCAL,
        required=False,
        allow_null=True,
        **kwargs,
    )


def check_manual_kcal(values):
    """Without kcal they follow from the macros (4/4/9 per gram); given kcal have to fit.

    Labels round and fiber adds energy, so only clearly too few kcal are rejected.
    """
    computed = kcal_from_macros(values)

    if values.get("kcal") is None:
        return {**values, "kcal": computed}

    if values["kcal"] < computed * Decimal("0.8") - 10:
        raise serializers.ValidationError(
            {
                "kcal": "Das passt nicht zu den Makros, "
                f"daraus ergeben sich etwa {computed:.0f} kcal."
            }
        )

    return values


class ManualFoodSerializer(serializers.Serializer):
    """A food the user types in: name and the values of the portion eaten."""

    food_name = serializers.CharField(max_length=255)
    kcal = manual_kcal()
    protein = manual_grams()
    carbs = manual_grams()
    fat = manual_grams()

    def validate(self, attrs):
        values = check_manual_kcal({key: attrs.get(key) for key in MACROS})

        return manual_snapshot(attrs["food_name"], values)


class ManualEntrySerializer(ManualFoodSerializer):
    consumed_on = serializers.DateField(validators=[not_in_future])
    meal_type = serializers.ChoiceField(choices=MealType)

    def validate(self, attrs):
        return {
            "consumed_on": attrs["consumed_on"],
            "meal_type": attrs["meal_type"],
            **super().validate(attrs),
        }


MANUAL_FIELDS = ("food_name", *MACROS)


class EntryPatchSerializer(serializers.Serializer):
    amount = AmountField(required=False)
    unit = serializers.ChoiceField(choices=FoodUnit, required=False)
    consumed_on = serializers.DateField(required=False, validators=[not_in_future])
    meal_type = serializers.ChoiceField(choices=MealType, required=False)
    # Only for foods the user typed in, see ManualFoodSerializer.
    food_name = serializers.CharField(max_length=255, required=False)
    kcal = manual_kcal()
    protein = manual_grams(required=False)
    carbs = manual_grams(required=False)
    fat = manual_grams(required=False)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Gib mindestens ein Feld an.")

        entry = self.instance
        changes_amount = "amount" in attrs or "unit" in attrs
        changes_values = any(field in attrs for field in MANUAL_FIELDS)

        if entry.source == TrackingEntry.Source.MANUAL:
            return self.validate_manual(entry, attrs, changes_amount)

        if changes_values:
            raise serializers.ValidationError(
                {
                    field: "Nur selbst eingetragene Lebensmittel lassen sich so ändern."
                    for field in MANUAL_FIELDS
                    if field in attrs
                }
            )

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
                **{
                    f"{key}_per_100": getattr(entry, f"{key}_per_100") for key in MACROS
                },
                "serving_quantity": entry.serving_quantity,
                "amount": attrs.get("amount", entry.amount),
                "unit": unit,
            }
            attrs.update(scaled_values(snapshot))

        return attrs

    def validate_manual(self, entry, attrs, changes_amount):
        if changes_amount:
            raise serializers.ValidationError(
                {
                    field: "Hier änderst du die Nährwerte statt der Menge."
                    for field in ("amount", "unit")
                    if field in attrs
                }
            )

        if not any(key in attrs for key in MACROS):
            return attrs

        values = {
            key: attrs[key] if key in attrs else getattr(entry, key) for key in MACROS
        }

        # Changed macros without kcal: the kcal follow them again.
        if "kcal" not in attrs:
            values["kcal"] = None

        return {**attrs, **check_manual_kcal(values)}

    def update(self, entry, validated_data):
        for field, value in validated_data.items():
            setattr(entry, field, value)

        entry.save()

        return entry


class ProductItemSerializer(serializers.Serializer):
    off_code = serializers.RegexField(PRODUCT_CODE_PATTERN)
    amount = AmountField()
    unit = serializers.ChoiceField(choices=FoodUnit)

    def validate(self, attrs):
        product = product_for(attrs["off_code"])
        check_unit(attrs["unit"], product.base_unit, product.serving_quantity)

        return snapshot_of(product, attrs["amount"], attrs["unit"])


class MealItemInputSerializer(serializers.Serializer):
    """A product with off_code, amount and unit, or an own item with name and values."""

    def to_internal_value(self, data):
        is_product = isinstance(data, dict) and "off_code" in data
        serializer = (ProductItemSerializer if is_product else ManualFoodSerializer)(
            data=data
        )
        serializer.is_valid(raise_exception=True)

        return serializer.validated_data


class MealInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    items = MealItemInputSerializer(many=True, min_length=1, max_length=50)


class MealItemSerializer(serializers.ModelSerializer):
    nutrition_per_100 = serializers.SerializerMethodField()

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

    def get_nutrition_per_100(self, item):
        return per_100_or_none(item)


class MealSerializer(serializers.ModelSerializer):
    items = MealItemSerializer(many=True, read_only=True)
    totals = MacrosSerializer(source="*", read_only=True)

    class Meta:
        model = Meal
        fields = ("id", "name", "items", "totals")


class FoodWeekSerializer(serializers.Serializer):
    iso_year = serializers.IntegerField()
    iso_week = serializers.IntegerField()
    week_start = serializers.DateField()
    week_end = serializers.DateField()
    # Days with entries and their average; days without entries do not count.
    days_count = serializers.IntegerField()
    average_kcal = serializers.DecimalField(max_digits=8, decimal_places=1)
