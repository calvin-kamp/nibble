import re

from rest_framework import serializers

from apps.foods.models import FoodProduct, FoodReport
from apps.foods.utils import BARCODE_PATTERN, normalize_barcode


class NutritionPer100Serializer(serializers.Serializer):
    """Reads the *_per_100 fields of products, entries and meal items."""

    kcal = serializers.DecimalField(
        source="kcal_per_100", max_digits=7, decimal_places=1, read_only=True
    )
    protein = serializers.DecimalField(
        source="protein_per_100", max_digits=7, decimal_places=1, read_only=True
    )
    carbs = serializers.DecimalField(
        source="carbs_per_100", max_digits=7, decimal_places=1, read_only=True
    )
    fat = serializers.DecimalField(
        source="fat_per_100", max_digits=7, decimal_places=1, read_only=True
    )


class FoodProductSerializer(serializers.ModelSerializer):
    nutrition_per_100 = NutritionPer100Serializer(source="*", read_only=True)

    class Meta:
        model = FoodProduct
        fields = (
            "code",
            "name",
            "brand",
            "generic",
            "base_unit",
            "nutrition_per_100",
            "serving_quantity",
            "package_quantity",
        )


class FoodSearchSerializer(serializers.Serializer):
    q = serializers.CharField(min_length=2, max_length=100, required=False)
    barcode = serializers.CharField(max_length=30, required=False)
    # Exact code of a product, also of generic foods without barcode, e.g. for recent foods.
    code = serializers.CharField(max_length=14, required=False)

    def validate_barcode(self, value):
        barcode = normalize_barcode(value)

        if not re.fullmatch(BARCODE_PATTERN, barcode):
            raise serializers.ValidationError("Ein Barcode hat 8 bis 14 Ziffern.")

        return barcode

    def validate(self, attrs):
        query = attrs.get("q")

        if not query and not attrs.get("barcode") and not attrs.get("code"):
            raise serializers.ValidationError(
                {"q": "Gib einen Suchtext oder einen Barcode an."}
            )

        # A barcode typed into the text search counts as barcode.
        if query and re.fullmatch(BARCODE_PATTERN, normalize_barcode(query)):
            attrs["barcode"] = normalize_barcode(query)
            del attrs["q"]

        return attrs


class FoodReportInputSerializer(serializers.Serializer):
    reason = serializers.ChoiceField(choices=FoodReport.Reason)
    comment = serializers.CharField(max_length=500, required=False, allow_blank=True, default="")
