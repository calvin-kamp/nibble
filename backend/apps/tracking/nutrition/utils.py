from decimal import Decimal

from rest_framework import serializers

from apps.tracking.models import FoodUnit
from apps.tracking.utils import round1

MACROS = ("kcal", "protein", "carbs", "fat")
MAX_VALUES = {"kcal": 100000, "protein": 10000, "carbs": 10000, "fat": 10000}
KCAL_PER_GRAM = {"protein": 4, "carbs": 4, "fat": 9}


def check_unit(unit, base_unit, serving_quantity):
    """g/ml must match the product, portion needs a serving size."""
    if unit == FoodUnit.PORTION:
        if serving_quantity is None:
            raise serializers.ValidationError(
                {"unit": "Für dieses Lebensmittel gibt es keine Portionsgröße."}
            )
    elif unit != base_unit:
        raise serializers.ValidationError(
            {"unit": f"Dieses Lebensmittel wird in {base_unit} angegeben."}
        )


def scaled_values(snapshot):
    """kcal and macros for amount and unit, from the stored values per 100.

    g/ml: per 100 × amount ÷ 100, portion: per 100 × amount × serving size ÷ 100.
    """
    quantity = snapshot["amount"]

    if snapshot["unit"] == FoodUnit.PORTION:
        quantity *= snapshot["serving_quantity"]

    values = {
        key: round1(snapshot[f"{key}_per_100"] * quantity / 100) for key in MACROS
    }

    if any(values[key] > MAX_VALUES[key] for key in MACROS):
        raise serializers.ValidationError({"amount": "Die Menge ist zu groß."})

    return values


def snapshot_of(product, amount, unit):
    """Copies the product into an entry or meal item and computes its values."""
    snapshot = {
        "off_code": product.code,
        "food_name": product.name,
        "brand": product.brand,
        "base_unit": product.base_unit,
        "serving_quantity": product.serving_quantity,
        "amount": amount,
        "unit": unit,
        **{f"{key}_per_100": getattr(product, f"{key}_per_100") for key in MACROS},
    }

    return {**snapshot, **scaled_values(snapshot)}


def kcal_from_macros(values):
    """Energy of protein, carbs and fat: 4, 4 and 9 kcal per gram."""
    return round1(sum(values[key] * factor for key, factor in KCAL_PER_GRAM.items()))


def manual_snapshot(food_name, values):
    """A typed-in food as an entry or meal item: one portion, no values per 100."""
    return {
        "off_code": None,
        "food_name": food_name,
        "brand": None,
        "base_unit": None,
        "serving_quantity": None,
        "amount": 1,
        "unit": FoodUnit.PORTION,
        **{f"{key}_per_100": None for key in MACROS},
        **{key: values[key] for key in MACROS},
    }


def total(items):
    """Sum of kcal and macros over entries, meal items or their validated dicts."""

    def value(item, key):
        return item[key] if isinstance(item, dict) else getattr(item, key)

    return {
        key: sum((value(item, key) for item in items), Decimal(0)) for key in MACROS
    }
