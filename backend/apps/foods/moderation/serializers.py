from decimal import Decimal

from rest_framework import serializers

from apps.foods.models import FoodProduct, FoodReport, MissingBarcode
from apps.foods.search.serializers import NutritionPer100Serializer
from config.fields import RoundedDecimalField

COUNTRIES = (
    ("en:germany", "Deutschland"),
    ("en:austria", "Österreich"),
    ("en:switzerland", "Schweiz"),
)

# Same limits as the import, see import_off_products.
MAX_KCAL_PER_100 = 900
MAX_GRAMS_PER_100 = 100
MAX_SERVING_QUANTITY = 5000
MAX_PACKAGE_QUANTITY = 100000


class MissingBarcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissingBarcode
        fields = ("code", "lookups", "first_searched_at", "last_searched_at")


class MissingBarcodeDetailSerializer(MissingBarcodeSerializer):
    off_product = serializers.SerializerMethodField()

    class Meta(MissingBarcodeSerializer.Meta):
        fields = MissingBarcodeSerializer.Meta.fields + ("off_product",)

    def get_off_product(self, missing):
        return self.context.get("off_product")


def grams(**kwargs):
    return RoundedDecimalField(
        decimal_places=1, min_value=0, max_value=MAX_GRAMS_PER_100, **kwargs
    )


class NutritionInputSerializer(serializers.Serializer):
    """Per 100 g or ml. nibble needs energy and the three macros only.

    The other fields of the EU declaration are optional: Open Food Facts accepts a product
    without them and keeps what it already has for fields that aren't sent.
    """

    kj = RoundedDecimalField(decimal_places=0, min_value=0, max_value=4000, required=False)
    kcal = RoundedDecimalField(decimal_places=1, min_value=0, max_value=MAX_KCAL_PER_100)
    fat = grams()
    saturated_fat = grams(required=False)
    carbs = grams()
    sugars = grams(required=False)
    fiber = grams(required=False)
    protein = grams()
    salt = RoundedDecimalField(
        decimal_places=2, min_value=0, max_value=MAX_GRAMS_PER_100, required=False
    )

    def validate(self, attrs):
        errors = {}

        if attrs.get("saturated_fat", 0) > attrs["fat"]:
            errors["saturated_fat"] = "Gesättigte Fettsäuren sind ein Teil des Fetts."

        if attrs.get("sugars", 0) > attrs["carbs"]:
            errors["sugars"] = "Zucker ist ein Teil der Kohlenhydrate."

        # A little slack for rounding on the packaging.
        if attrs["fat"] + attrs["carbs"] + attrs["protein"] > MAX_GRAMS_PER_100 + 5:
            errors["carbs"] = "Fett, Kohlenhydrate und Eiweiß ergeben mehr als 100 g."

        if errors:
            raise serializers.ValidationError(errors)

        return attrs


class FoodProductInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    brand = serializers.CharField(max_length=255, required=False, allow_blank=True)
    base_unit = serializers.ChoiceField(choices=FoodProduct.BaseUnit)
    package_quantity = RoundedDecimalField(
        decimal_places=2,
        min_value=Decimal("0.01"),
        max_value=MAX_PACKAGE_QUANTITY,
        required=False,
        allow_null=True,
    )
    serving_quantity = RoundedDecimalField(
        decimal_places=2,
        min_value=Decimal("0.01"),
        max_value=MAX_SERVING_QUANTITY,
        required=False,
        allow_null=True,
    )
    countries = serializers.ListField(
        child=serializers.ChoiceField(choices=COUNTRIES),
        min_length=1,
        max_length=len(COUNTRIES),
    )
    nutrition_per_100 = NutritionInputSerializer()

    def validate_name(self, value):
        return value.strip()

    def validate_brand(self, value):
        return value.strip()

    def validate_countries(self, value):
        return list(dict.fromkeys(value))


class FoodProductUpdateSerializer(serializers.Serializer):
    """Correction of a product. Name and brand stay in nibble, the rest goes to OFF too."""

    name = serializers.CharField(max_length=255)
    brand = serializers.CharField(max_length=255, required=False, allow_blank=True)
    base_unit = serializers.ChoiceField(choices=FoodProduct.BaseUnit)
    package_quantity = RoundedDecimalField(
        decimal_places=2,
        min_value=Decimal("0.01"),
        max_value=MAX_PACKAGE_QUANTITY,
        required=False,
        allow_null=True,
    )
    serving_quantity = RoundedDecimalField(
        decimal_places=2,
        min_value=Decimal("0.01"),
        max_value=MAX_SERVING_QUANTITY,
        required=False,
        allow_null=True,
    )
    nutrition_per_100 = NutritionInputSerializer()

    def validate_name(self, value):
        return value.strip()

    def validate_brand(self, value):
        return value.strip()


class FoodReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodReport
        fields = ("id", "reason", "comment", "created_at")


class ReportedProductSerializer(serializers.ModelSerializer):
    """A product with open reports, for the list in the admin."""

    report_count = serializers.IntegerField(read_only=True)
    last_reported_at = serializers.DateTimeField(read_only=True)
    reasons = serializers.SerializerMethodField()

    class Meta:
        model = FoodProduct
        fields = ("code", "name", "brand", "generic", "report_count", "last_reported_at", "reasons")

    def get_reasons(self, product):
        return sorted({report.reason for report in product.reports.all()})


class ModerationProductSerializer(serializers.ModelSerializer):
    """A product with everything staff need to correct it."""

    nutrition_per_100 = NutritionPer100Serializer(source="*", read_only=True)
    reports = FoodReportSerializer(many=True, read_only=True)

    class Meta:
        model = FoodProduct
        fields = (
            "code",
            "name",
            "brand",
            "generic",
            "base_unit",
            "serving_quantity",
            "package_quantity",
            "nutrition_per_100",
            "curated_at",
            "reports",
        )
