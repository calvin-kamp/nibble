from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.foods import off
from apps.foods.exceptions import OffUnavailable, ProductExists
from apps.foods.models import FoodProduct, FoodReport, MissingBarcode
from apps.foods.utils import has_valid_check_digit


def record_missing_barcode(code):
    """Counts a barcode lookup without result. Stores nothing about who searched."""
    if not has_valid_check_digit(code):
        return

    updated = MissingBarcode.objects.filter(code=code).update(
        lookups=F("lookups") + 1, last_searched_at=timezone.now()
    )

    if not updated:
        MissingBarcode.objects.get_or_create(code=code)


def add_product(data, profile):
    """Saves a product staff entered, on Open Food Facts first and then here.

    Without an OFF account in the settings only the own database gets it.
    Returns the product and whether OFF has it.
    """
    code = data["code"]

    if FoodProduct.objects.filter(code=code).exists():
        MissingBarcode.objects.filter(code=code).delete()

        raise ProductExists()

    synced = off.is_write_configured()

    if synced:
        try:
            off.save_product(data, profile)
        except off.OffError as exc:
            raise OffUnavailable() from exc

    now = timezone.now()

    with transaction.atomic():
        product = FoodProduct.objects.create(
            code=code, imported_at=now, curated_at=now, **product_values(data)
        )
        MissingBarcode.objects.filter(code=code).delete()

    return product, synced


def product_values(data):
    nutrition = data["nutrition_per_100"]

    return {
        "name": data["name"],
        "brand": data.get("brand") or None,
        "base_unit": data["base_unit"],
        "kcal_per_100": nutrition["kcal"],
        "protein_per_100": nutrition["protein"],
        "carbs_per_100": nutrition["carbs"],
        "fat_per_100": nutrition["fat"],
        "serving_quantity": data.get("serving_quantity"),
        "package_quantity": data.get("package_quantity"),
    }


def update_product(product, data, profile):
    """Saves a correction staff made and closes the product's reports.

    Values and amounts go to Open Food Facts first, name and brand only stay here. Generic
    foods are nibble's own and never go there. Returns whether OFF has the correction.
    """
    synced = not product.generic and off.is_write_configured()

    if synced:
        try:
            off.save_product({**data, "code": product.code}, profile, with_name=False)
        except off.OffError as exc:
            raise OffUnavailable() from exc

    with transaction.atomic():
        for field, value in product_values(data).items():
            setattr(product, field, value)

        # From now on the import leaves it alone, see import_off_products.
        product.curated_at = timezone.now()
        product.save()
        product.reports.all().delete()

    return synced


def add_generic_product(data):
    """Loose food without a barcode, e.g. a banana. Stays in nibble only."""
    prefix = FoodProduct.GENERIC_CODE_PREFIX
    codes = FoodProduct.objects.filter(generic=True, code__startswith=prefix).values_list(
        "code", flat=True
    )
    numbers = [int(code[len(prefix) :]) for code in codes if code[len(prefix) :].isdigit()]
    now = timezone.now()

    return FoodProduct.objects.create(
        code=f"{prefix}{max(numbers, default=0) + 1:05d}",
        generic=True,
        imported_at=now,
        curated_at=now,
        **product_values(data),
    )


def report_product(product, reason, comment=""):
    """Stores a user's hint that something is wrong, without who sent it."""
    return FoodReport.objects.create(product=product, reason=reason, comment=comment.strip())
