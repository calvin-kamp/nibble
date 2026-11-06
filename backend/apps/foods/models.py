from django.contrib.postgres.indexes import GinIndex, OpClass
from django.db import models
from django.db.models.functions import Upper


def per_100_field():
    return models.DecimalField(
        max_digits=7,
        decimal_places=1,
    )


class FoodProduct(models.Model):
    """Product from the Open Food Facts export (DE, AT, CH), see import_off_products.

    Staff can add a product that is missing or correct one; both are sent to Open Food Facts
    as well. Generic foods without a barcode (loose fruit, vegetables) are nibble's own, their
    code starts with GENERIC_CODE_PREFIX and they never go to Open Food Facts.
    """

    GENERIC_CODE_PREFIX = "n"

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

    # Loose food without a barcode, e.g. a banana; listed first in the search.
    generic = models.BooleanField(default=False)

    # Products missing from the latest dump are removed after the import.
    imported_at = models.DateTimeField()
    # Added or corrected by staff in the admin. The import neither deletes nor changes it,
    # the values staff checked against the packaging win over the export.
    curated_at = models.DateTimeField(
        blank=True,
        null=True,
    )

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


class MissingBarcode(models.Model):
    """Barcode someone looked up without a result, for staff to add.

    Holds no reference to who searched: only the barcode, how often and when.
    """

    code = models.CharField(
        max_length=14,
        primary_key=True,
    )
    lookups = models.PositiveIntegerField(default=1)
    first_searched_at = models.DateTimeField(auto_now_add=True)
    last_searched_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-lookups", "-last_searched_at"]

    def __str__(self):
        return self.code


class FoodReport(models.Model):
    """A user's hint that something about a product is wrong, for staff to check.

    Holds no reference to who reported: only the product, what is wrong and when.
    """

    class Reason(models.TextChoices):
        NUTRITION = "nutrition", "Nährwerte falsch"
        UNIT = "unit", "Gramm und Milliliter vertauscht"
        QUANTITY = "quantity", "Portion oder Packung falsch"
        NAME = "name", "Name oder Marke falsch"
        OTHER = "other", "Etwas anderes"

    product = models.ForeignKey(
        FoodProduct,
        on_delete=models.CASCADE,
        related_name="reports",
    )
    reason = models.CharField(
        choices=Reason,
        max_length=20,
    )
    comment = models.CharField(
        max_length=500,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product_id}: {self.reason}"
