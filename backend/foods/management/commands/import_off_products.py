"""Imports the products sold in Germany, Austria and Switzerland from Open Food Facts.

Reads the CSV export (tab separated, gzip) as a stream, so the file is never
stored. Only products with a name and all four nutrients pass, values that
can't be right (e.g. 120 g fat per 100 g) are dropped. Products nobody has
scanned in the last years are most likely no longer sold and are skipped too.
Products missing from the export are deleted at the end; tracked entries keep
their own copy.

Run with ``manage.py import_off_products [--source URL_OR_PATH] [--limit N]
[--scan-years N]``.
"""

import gzip
import io
import re
import urllib.request
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from foods.models import FoodProduct

COUNTRIES = {"en:germany", "en:austria", "en:switzerland"}
# Cheap check on the raw line before splitting it.
COUNTRY_MARKERS = tuple(COUNTRIES)

CODE_PATTERN = re.compile(r"^[0-9]{8,14}$")
LIQUID_QUANTITY_PATTERN = re.compile(r"\d\s*(ml|cl|dl|l)\b", re.IGNORECASE)
# popularity_tags names the years with scans, e.g. "top-75-percent-scans-2025".
SCAN_YEAR_PATTERN = re.compile(r"-scans-(\d{4})\b")

NUTRIMENTS = {
    "kcal_per_100": "energy-kcal_100g",
    "protein_per_100": "proteins_100g",
    "carbs_per_100": "carbohydrates_100g",
    "fat_per_100": "fat_100g",
}

# The only columns of the export the import reads.
COLUMNS = (
    "code",
    "product_name",
    "brands",
    "countries_tags",
    "quantity",
    "product_quantity",
    "serving_quantity",
    "popularity_tags",
    *NUTRIMENTS.values(),
)

MAX_KCAL_PER_100 = 900
MAX_GRAMS_PER_100 = 100
MAX_SERVING_QUANTITY = 5000
MAX_PACKAGE_QUANTITY = 100000

DEFAULT_SCAN_YEARS = 2

BATCH_SIZE = 2000
UPDATE_FIELDS = (
    "name",
    "brand",
    "base_unit",
    *NUTRIMENTS,
    "serving_quantity",
    "package_quantity",
    "imported_at",
)


def to_decimal(value, places="0.1"):
    try:
        number = Decimal(str(value))

        return number.quantize(Decimal(places)) if number.is_finite() else None
    except (InvalidOperation, TypeError, ValueError):
        return None


def quantity_or_none(value, maximum):
    """Positive amount in g or ml up to maximum, None otherwise."""
    quantity = to_decimal(value, "0.01") if value else None

    if quantity is None or not 0 < quantity <= maximum:
        return None

    return quantity


def is_plausible(values):
    if any(value < 0 for value in values.values()):
        return False

    if values["kcal_per_100"] > MAX_KCAL_PER_100:
        return False

    grams = (values["protein_per_100"], values["carbs_per_100"], values["fat_per_100"])

    # A little slack for rounding on the packaging.
    return max(grams) <= MAX_GRAMS_PER_100 and sum(grams) <= MAX_GRAMS_PER_100 + 5


def base_unit(row):
    """Drinks are measured in ml, everything else in g."""
    if LIQUID_QUANTITY_PATTERN.search(row["quantity"]):
        return FoodProduct.BaseUnit.ML

    return FoodProduct.BaseUnit.G


def first_brand(row):
    brand = row["brands"].split(",")[0].strip()

    return brand[:255] or None


def last_scan_year(popularity_tags):
    """Latest year someone scanned the product, None if never."""
    return max(map(int, SCAN_YEAR_PATTERN.findall(popularity_tags)), default=None)


def parse_product(row, imported_at, min_scan_year=None):
    """FoodProduct for a row of the export, or None if it doesn't qualify."""
    code = row["code"].strip()

    if not CODE_PATTERN.match(code):
        return None

    if not COUNTRIES & set(row["countries_tags"].split(",")):
        return None

    if min_scan_year is not None:
        scanned = last_scan_year(row["popularity_tags"])

        if scanned is None or scanned < min_scan_year:
            return None

    name = row["product_name"].strip()

    if not name:
        return None

    values = {field: to_decimal(row[column]) for field, column in NUTRIMENTS.items()}

    if None in values.values() or not is_plausible(values):
        return None

    return FoodProduct(
        code=code,
        name=name[:255],
        brand=first_brand(row),
        base_unit=base_unit(row),
        serving_quantity=quantity_or_none(row["serving_quantity"], MAX_SERVING_QUANTITY),
        package_quantity=quantity_or_none(row["product_quantity"], MAX_PACKAGE_QUANTITY),
        imported_at=imported_at,
        **values,
    )


@contextmanager
def open_export(source):
    """Yields the lines of the export as text, from a URL or a local file."""
    if source.startswith(("http://", "https://")):
        with urllib.request.urlopen(source) as response:
            with gzip.GzipFile(fileobj=response) as raw:
                yield io.TextIOWrapper(raw, encoding="utf-8", errors="replace")
    elif source.endswith(".gz"):
        with gzip.open(source, "rt", encoding="utf-8", errors="replace") as lines:
            yield lines
    else:
        with open(source, encoding="utf-8", errors="replace") as lines:
            yield lines


def column_indexes(header):
    names = header.rstrip("\n").split("\t")
    missing = [column for column in COLUMNS if column not in names]

    if missing:
        raise CommandError(f"Columns missing in the export: {', '.join(missing)}")

    return len(names), {column: names.index(column) for column in COLUMNS}


def save_batch(products):
    # The export can contain a code twice; one row per code and batch.
    unique = {product.code: product for product in products}

    FoodProduct.objects.bulk_create(
        unique.values(),
        update_conflicts=True,
        unique_fields=["code"],
        update_fields=UPDATE_FIELDS,
    )

    return len(unique)


class Command(BaseCommand):
    help = "Imports DE/AT/CH products from the Open Food Facts CSV export."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            default=settings.OFF_DUMP_URL,
            help="URL or path of the CSV export (.csv or .csv.gz).",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Stop after this many products and keep all others (for development).",
        )
        parser.add_argument(
            "--scan-years",
            type=int,
            default=DEFAULT_SCAN_YEARS,
            help="Only products scanned in this many past years (and this one); 0 imports all.",
        )

    def handle(self, *args, source, limit, scan_years, **options):
        imported_at = timezone.now()
        min_scan_year = imported_at.year - scan_years if scan_years > 0 else None
        imported = 0
        batch = []

        self.stdout.write(f"Reading {source} ...")

        with open_export(source) as lines:
            column_count, indexes = column_indexes(next(lines, ""))

            for line in lines:
                if not any(marker in line for marker in COUNTRY_MARKERS):
                    continue

                fields = line.rstrip("\n").split("\t")

                if len(fields) != column_count:
                    continue

                row = {column: fields[index] for column, index in indexes.items()}
                product = parse_product(row, imported_at, min_scan_year)

                if product is None:
                    continue

                batch.append(product)

                if len(batch) >= BATCH_SIZE:
                    imported += save_batch(batch)
                    batch = []

                if limit and imported + len(batch) >= limit:
                    break

        if batch:
            imported += save_batch(batch)

        removed = 0

        # A partial run must not throw away the products it didn't reach.
        if not limit:
            removed, _ = FoodProduct.objects.filter(imported_at__lt=imported_at).delete()

        self.stdout.write(
            self.style.SUCCESS(f"{imported} products imported, {removed} removed.")
        )
