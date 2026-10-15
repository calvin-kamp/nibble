from decimal import ROUND_HALF_UP

from rest_framework import serializers

from food.models import Food


def nutrient_field():
    return serializers.DecimalField(
        max_digits=8,
        decimal_places=1,
        coerce_to_string=False,
        read_only=True,
        # Like round_nutrient, so totals and single values round alike.
        rounding=ROUND_HALF_UP,
    )


class NutrientsSerializer(serializers.Serializer):
    """Reads a dict with kcal, protein, carbs and fat."""

    kcal = nutrient_field()
    protein = nutrient_field()
    carbs = nutrient_field()
    fat = nutrient_field()


class UnitSerializer(serializers.Serializer):
    """{key: "slice", name: "Scheibe", amount: 25} – amount in the food's basis."""

    key = serializers.CharField()
    name = serializers.CharField()
    amount = serializers.DecimalField(
        max_digits=6, decimal_places=1, coerce_to_string=False
    )


def unit_options(food):
    """The base unit first, then the household measures stored for the food."""
    base = {"key": food.basis, "name": food.basis, "amount": 1}
    units = [
        {"key": unit.kind, "name": unit.get_kind_display(), "amount": unit.amount}
        for unit in food.units.all()
    ]

    return [base, *units]


class FoodSerializer(serializers.ModelSerializer):
    per_100 = NutrientsSerializer(read_only=True)
    units = serializers.SerializerMethodField()

    class Meta:
        model = Food
        fields = ("id", "name", "brand", "basis", "per_100", "units")

    def get_units(self, food):
        return UnitSerializer(unit_options(food), many=True).data
