from decimal import ROUND_HALF_UP, Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

KCAL_MAX_PER_100 = 900
MACRO_MAX_PER_100 = 100

NUTRIENTS = ("kcal", "protein", "carbs", "fat")

ONE_DECIMAL = Decimal("0.1")


def per_100_field(maximum):
    return models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(maximum)],
    )


def round_nutrient(value):
    """One decimal, rounded like a nutrition label (0.25 → 0.3)."""
    return Decimal(value).quantize(ONE_DECIMAL, rounding=ROUND_HALF_UP)


class Basis(models.TextChoices):
    """What the values per 100 refer to; also the base unit of amounts."""

    GRAM = "g", "g"
    MILLILITRE = "ml", "ml"


class NutrientsPer100(models.Model):
    """kcal and macros per 100 g or 100 ml.

    Shared by foods and by the copies in diary entries, which keep the values a
    food had when it was logged.
    """

    basis = models.CharField(max_length=2, choices=Basis, default=Basis.GRAM)
    kcal_per_100 = per_100_field(KCAL_MAX_PER_100)
    protein_per_100 = per_100_field(MACRO_MAX_PER_100)
    carbs_per_100 = per_100_field(MACRO_MAX_PER_100)
    fat_per_100 = per_100_field(MACRO_MAX_PER_100)

    class Meta:
        abstract = True

    @property
    def per_100(self):
        return {name: getattr(self, f"{name}_per_100") for name in NUTRIENTS}

    def nutrients_for(self, amount):
        """Unrounded values for an amount in the basis unit (grams or millilitres)."""
        factor = Decimal(amount) / 100

        return {name: value * factor for name, value in self.per_100.items()}


class Food(NutrientsPer100):
    """A product of the shared food database, values as printed on the pack."""

    class Source(models.TextChoices):
        OPEN_FOOD_FACTS = "off", "Open Food Facts"
        NIBBLE = "nibble", "Nibble"

    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=120, blank=True)
    # EAN-8, UPC-A, EAN-13 or GTIN-14, digits only; basic foods have none.
    barcode = models.CharField(max_length=14, unique=True, null=True, blank=True)
    source = models.CharField(max_length=6, choices=Source, default=Source.NIBBLE)
    # Unique scans on Open Food Facts; well-known products come first in the search.
    popularity = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name", "brand"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "brand"],
                condition=models.Q(barcode__isnull=True),
                name="food_unique_name_brand_without_barcode",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.brand})" if self.brand else self.name


class FoodUnit(models.Model):
    """A household measure of a food, e.g. "Scheibe · 25 g".

    The base unit (g or ml, see Food.basis) is always available and not stored.
    """

    class Kind(models.TextChoices):
        PORTION = "portion", "Portion"
        PIECE = "piece", "Stück"
        SLICE = "slice", "Scheibe"
        TABLESPOON = "tablespoon", "Esslöffel"

    food = models.ForeignKey(Food, related_name="units", on_delete=models.CASCADE)
    kind = models.CharField(max_length=10, choices=Kind)
    # In the food's basis unit.
    amount = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.1"))],
    )

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(fields=["food", "kind"], name="food_unit_once"),
        ]

    def __str__(self):
        return f"{self.get_kind_display()} · {self.amount} {self.food.basis}"
