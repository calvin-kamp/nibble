from rest_framework import serializers

from .fields import RoundedDecimalField


class MacrosSerializer(serializers.Serializer):
    """kcal plus protein, carbs and fat in grams, see the Macros schema."""

    kcal = RoundedDecimalField(decimal_places=1, min_value=0, max_value=100000)
    protein = RoundedDecimalField(decimal_places=1, min_value=0, max_value=10000)
    carbs = RoundedDecimalField(decimal_places=1, min_value=0, max_value=10000)
    fat = RoundedDecimalField(decimal_places=1, min_value=0, max_value=10000)
