from django.contrib.postgres.indexes import GinIndex, OpClass
from django.db import models
from django.db.models.functions import Upper


def per_100_field():
    return models.DecimalField(
        max_digits=7,
        decimal_places=1,
    )


class FoodProduct(models.Model):
    """Product from the Open Food Facts export (DE, AT, CH), see import_off_products."""

    class BaseUnit(models.TextChoices):
        G = "g", "g"
        ML = "ml", "ml"

    code = models.CharField(
        max_length=14,
        primary_key=True,
    )
    name = models.CharField(max_length=255)
    brand = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    base_unit = models.CharField(
        choices=BaseUnit,
        default=BaseUnit.G,
        max_length=2,
    )

    kcal_per_100 = per_100_field()
    protein_per_100 = per_100_field()
    carbs_per_100 = per_100_field()
    fat_per_100 = per_100_field()

    # Both in base_unit (g or ml), None if OFF doesn't know them.
    serving_quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
    )
    package_quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
    )

    # Products missing from the latest dump are removed after the import.
    imported_at = models.DateTimeField()

    class Meta:
        ordering = ["name", "code"]
        indexes = [
            # icontains compiles to UPPER(name) LIKE ..., which this index serves.
            GinIndex(
                OpClass(Upper("name"), name="gin_trgm_ops"),
                name="foodproduct_name_trgm",
            ),
            GinIndex(
                OpClass(Upper("brand"), name="gin_trgm_ops"),
                name="foodproduct_brand_trgm",
            ),
        ]

    def __str__(self):
        return self.name
