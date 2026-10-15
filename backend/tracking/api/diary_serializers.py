from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from food.api.serializers import (
    FoodSerializer,
    NutrientsSerializer,
    UnitSerializer,
    unit_options,
)
from food.models import Food
from tracking.models import (
    AMOUNT_MAX,
    SERVINGS_MAX,
    SERVINGS_MIN,
    SERVINGS_STEP,
    DiaryEntry,
    DiaryEntryItem,
    Meal,
    Section,
)

QUANTITY_MESSAGE = "Gib eine Menge größer als 0 ein."
SERVINGS_MESSAGE = "Wähle 0,5 bis 20 Portionen in halben Schritten."
# Logging ahead (planning) is allowed, within reason.
DATE_RANGE_DAYS = 400


def validate_date(value):
    today = timezone.localdate()

    if abs((value - today).days) > DATE_RANGE_DAYS:
        raise serializers.ValidationError("Wähle ein Datum im Umkreis eines Jahres.")

    return value


def validate_servings(value):
    if value % SERVINGS_STEP:
        raise serializers.ValidationError(SERVINGS_MESSAGE)

    return value


def servings_field(**kwargs):
    return serializers.DecimalField(
        max_digits=3,
        decimal_places=1,
        min_value=SERVINGS_MIN,
        max_value=Decimal(SERVINGS_MAX),
        coerce_to_string=False,
        validators=[validate_servings],
        error_messages={
            "min_value": SERVINGS_MESSAGE,
            "max_value": SERVINGS_MESSAGE,
            "invalid": SERVINGS_MESSAGE,
        },
        **kwargs,
    )


def quantity_field(**kwargs):
    return serializers.DecimalField(
        max_digits=7,
        decimal_places=1,
        min_value=Decimal("0.1"),
        coerce_to_string=False,
        error_messages={"min_value": QUANTITY_MESSAGE, "invalid": QUANTITY_MESSAGE},
        **kwargs,
    )


def entry_units(entry):
    """Units to choose from when editing: the food's current ones, or the copy."""
    if entry.food is not None:
        return unit_options(entry.food)

    base = {"key": entry.items.all()[0].basis, "name": entry.items.all()[0].basis}
    units = [{**base, "amount": Decimal(1)}]

    if entry.unit_key != base["key"]:
        units.append(
            {
                "key": entry.unit_key,
                "name": entry.unit_name,
                "amount": entry.unit_amount,
            }
        )

    return units


def resolve_unit(units, key):
    unit = next((unit for unit in units if unit["key"] == key), None)

    if unit is None:
        raise serializers.ValidationError(
            {"unit": ["Diese Einheit gibt es hier nicht."]}
        )

    return unit


def check_amount(quantity, unit):
    if quantity * unit["amount"] > AMOUNT_MAX:
        raise serializers.ValidationError(
            {"quantity": [f"Höchstens {AMOUNT_MAX:,} g bzw. ml.".replace(",", ".")]}
        )


class EntryItemSerializer(serializers.Serializer):
    """An ingredient of a meal entry, scaled to the logged servings (read-only)."""

    name = serializers.CharField()
    brand = serializers.CharField()
    basis = serializers.CharField()
    amount = serializers.DecimalField(
        max_digits=9, decimal_places=1, coerce_to_string=False
    )
    nutrients = NutrientsSerializer()


class DiaryEntrySerializer(serializers.ModelSerializer):
    """One line of the day, everything the diary and the edit sheet show."""

    basis = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    units = serializers.SerializerMethodField()
    nutrients = serializers.SerializerMethodField()
    per_100 = serializers.SerializerMethodField()
    per_serving = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    quantity = serializers.DecimalField(
        max_digits=7, decimal_places=1, coerce_to_string=False, read_only=True
    )
    servings = serializers.DecimalField(
        max_digits=3, decimal_places=1, coerce_to_string=False, read_only=True
    )

    class Meta:
        model = DiaryEntry
        fields = (
            "id",
            "date",
            "section",
            "kind",
            "name",
            "brand",
            "food",
            "meal",
            "basis",
            "quantity",
            "unit",
            "units",
            "servings",
            "nutrients",
            "per_100",
            "per_serving",
            "items",
        )
        read_only_fields = fields

    def _is_food(self, entry):
        return entry.kind == DiaryEntry.Kind.FOOD

    def get_basis(self, entry):
        """g or ml of the logged food; None for meals (their foods differ)."""
        return entry.items.all()[0].basis if self._is_food(entry) else None

    def get_unit(self, entry):
        if not self._is_food(entry):
            return None

        return UnitSerializer(
            {
                "key": entry.unit_key,
                "name": entry.unit_name,
                "amount": entry.unit_amount,
            }
        ).data

    def get_units(self, entry):
        if not self._is_food(entry):
            return None

        return UnitSerializer(entry_units(entry), many=True).data

    def get_nutrients(self, entry):
        return NutrientsSerializer(entry.nutrients(entry.items.all())).data

    def get_per_100(self, entry):
        if not self._is_food(entry):
            return None

        return NutrientsSerializer(entry.items.all()[0].per_100).data

    def get_per_serving(self, entry):
        if self._is_food(entry):
            return None

        totals = dict.fromkeys(("kcal", "protein", "carbs", "fat"), Decimal(0))

        for item in entry.items.all():
            for name, value in item.nutrients_for(item.amount).items():
                totals[name] += value

        return NutrientsSerializer(totals).data

    def get_items(self, entry):
        if self._is_food(entry):
            return []

        return EntryItemSerializer(
            [
                {
                    "name": item.name,
                    "brand": item.brand,
                    "basis": item.basis,
                    "amount": item.amount * entry.servings,
                    "nutrients": item.nutrients_for(item.amount * entry.servings),
                }
                for item in entry.items.all()
            ],
            many=True,
        ).data


class DiaryEntryCreateSerializer(serializers.Serializer):
    """Logs a food (quantity + unit) or one of the user's meals (servings)."""

    date = serializers.DateField(validators=[validate_date])
    section = serializers.ChoiceField(choices=Section.choices)
    food = serializers.PrimaryKeyRelatedField(
        queryset=Food.objects.prefetch_related("units"), required=False
    )
    quantity = quantity_field(required=False)
    unit = serializers.CharField(required=False)
    meal = serializers.PrimaryKeyRelatedField(
        queryset=Meal.objects.none(), required=False
    )
    servings = servings_field(required=False)

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")

        # Someone else's meal looks exactly like a missing one.
        if request is not None:
            fields["meal"].queryset = Meal.objects.filter(
                owner=request.user
            ).prefetch_related("items__food")

        return fields

    def validate(self, attrs):
        food, meal = attrs.get("food"), attrs.get("meal")

        if (food is None) == (meal is None):
            raise serializers.ValidationError(
                "Wähle entweder ein Lebensmittel oder eine Mahlzeit."
            )

        if food is not None:
            if attrs.get("quantity") is None:
                raise serializers.ValidationError({"quantity": [QUANTITY_MESSAGE]})

            unit = resolve_unit(unit_options(food), attrs.get("unit", food.basis))
            check_amount(attrs["quantity"], unit)
            attrs["unit"] = unit
        else:
            if attrs.get("servings") is None:
                raise serializers.ValidationError({"servings": [SERVINGS_MESSAGE]})

            if not meal.items.all():
                raise serializers.ValidationError(
                    {"meal": ["Diese Mahlzeit enthält keine Lebensmittel."]}
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        owner = self.context["request"].user
        common = {
            "owner": owner,
            "date": validated_data["date"],
            "section": validated_data["section"],
        }

        if "food" in validated_data:
            food, unit = validated_data["food"], validated_data["unit"]
            entry = DiaryEntry.objects.create(
                **common,
                kind=DiaryEntry.Kind.FOOD,
                name=food.name,
                brand=food.brand,
                food=food,
                quantity=validated_data["quantity"],
                unit_key=unit["key"],
                unit_name=unit["name"],
                unit_amount=unit["amount"],
            )
            item = DiaryEntryItem.copy_of(
                food, validated_data["quantity"] * unit["amount"]
            )
            item.entry = entry
            item.save()

            return entry

        meal = validated_data["meal"]
        entry = DiaryEntry.objects.create(
            **common,
            kind=DiaryEntry.Kind.MEAL,
            name=meal.name,
            meal=meal,
            servings=validated_data["servings"],
        )
        items = [
            DiaryEntryItem.copy_of(item.food, item.amount) for item in meal.items.all()
        ]

        for item in items:
            item.entry = entry

        DiaryEntryItem.objects.bulk_create(items)

        return entry


class DiaryEntryUpdateSerializer(serializers.Serializer):
    """Section always; quantity and unit for foods, servings for meals."""

    section = serializers.ChoiceField(choices=Section.choices, required=False)
    quantity = quantity_field(required=False)
    unit = serializers.CharField(required=False)
    servings = servings_field(required=False)

    def validate(self, attrs):
        entry = self.instance
        is_food = entry.kind == DiaryEntry.Kind.FOOD

        if is_food and "servings" in attrs:
            raise serializers.ValidationError({"servings": ["Nur bei Mahlzeiten."]})

        if not is_food and ({"quantity", "unit"} & attrs.keys()):
            raise serializers.ValidationError(
                "Bei Mahlzeiten änderst du die Portionen."
            )

        if is_food and ({"quantity", "unit"} & attrs.keys()):
            unit = resolve_unit(entry_units(entry), attrs.get("unit", entry.unit_key))
            quantity = attrs.get("quantity", entry.quantity)
            check_amount(quantity, unit)
            attrs["unit"] = unit
            attrs["quantity"] = quantity

        return attrs

    @transaction.atomic
    def update(self, entry, validated_data):
        entry.section = validated_data.get("section", entry.section)

        if "servings" in validated_data:
            entry.servings = validated_data["servings"]

        if "unit" in validated_data:
            unit = validated_data["unit"]
            entry.quantity = validated_data["quantity"]
            entry.unit_key = unit["key"]
            entry.unit_name = unit["name"]
            entry.unit_amount = unit["amount"]
            DiaryEntryItem.objects.filter(entry=entry).update(
                amount=entry.quantity * entry.unit_amount
            )

        entry.save()

        return entry


class DaySectionSerializer(serializers.Serializer):
    key = serializers.CharField()
    name = serializers.CharField()
    totals = NutrientsSerializer()
    entries = DiaryEntrySerializer(many=True)


class GoalsSerializer(serializers.Serializer):
    kcal = serializers.IntegerField()
    protein = serializers.IntegerField(allow_null=True)
    carbs = serializers.IntegerField(allow_null=True)
    fat = serializers.IntegerField(allow_null=True)


class DiaryDaySerializer(serializers.Serializer):
    date = serializers.DateField()
    goals = GoalsSerializer(allow_null=True)
    totals = NutrientsSerializer()
    sections = DaySectionSerializer(many=True)


class SectionSummarySerializer(serializers.Serializer):
    key = serializers.CharField()
    name = serializers.CharField()
    count = serializers.IntegerField()
    kcal = serializers.DecimalField(
        max_digits=8, decimal_places=1, coerce_to_string=False
    )


class DiarySummarySerializer(serializers.Serializer):
    """For the dashboard: no entries, only totals per section and day."""

    date = serializers.DateField()
    goals = GoalsSerializer(allow_null=True)
    totals = NutrientsSerializer()
    sections = SectionSummarySerializer(many=True)


class RecentFoodSerializer(serializers.Serializer):
    """A food logged recently, with the amount used last time."""

    food = FoodSerializer()
    quantity = serializers.DecimalField(
        max_digits=7, decimal_places=1, coerce_to_string=False
    )
    unit = UnitSerializer()
    nutrients = NutrientsSerializer()


def recent_food_data(entry):
    """Last quantity and unit; falls back to the base unit if the unit is gone."""
    food = entry.food
    units = unit_options(food)
    unit = next((u for u in units if u["key"] == entry.unit_key), None)
    quantity = entry.quantity

    if unit is None:
        unit, quantity = units[0], entry.quantity * entry.unit_amount

    return {
        "food": food,
        "quantity": quantity,
        "unit": unit,
        "nutrients": food.nutrients_for(quantity * unit["amount"]),
    }
