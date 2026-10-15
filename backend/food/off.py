"""Reads the Open Food Facts CSV export and keeps what Nibble needs.

The export (en.openfoodfacts.org.products.csv.gz, about 200 tab-separated
columns, millions of rows) is trimmed to products sold in the given countries
that have a name and complete, plausible values per 100 g or 100 ml, and to
ten columns:

    barcode, name, brand, basis, kcal, protein, carbs, fat, serving, scans

``basis`` is "ml" when the pack size is a volume (e.g. "1 l"), else "g".
``serving`` is the portion in that unit, empty if the product names none.

Product data: Open Food Facts, https://world.openfoodfacts.org, licensed under
the Open Database License (ODbL). The app names this source in the search.
"""

import csv
import gzip
import re
import sys
from dataclasses import astuple, dataclass, fields

from food.models import KCAL_MAX_PER_100, MACRO_MAX_PER_100, Basis

DEFAULT_COUNTRIES = frozenset({"en:germany", "en:austria", "en:switzerland"})

NAME_MAX_LENGTH = 200
BRAND_MAX_LENGTH = 120

KJ_PER_KCAL = 4.184

# Per 100 g the macros can't weigh more than 100 g; a little slack for rounding.
MACRO_SUM_MAX = 101

# A portion outside this range is a typo in the source, not a portion.
SERVING_MIN = 1
SERVING_MAX = 2000

# EAN-8, UPC-A, EAN-13 and GTIN-14; shorter codes are shop-internal.
BARCODE_PATTERN = re.compile(r"^\d{8,14}$")

# "1 l", "330ml", "6 x 0,33 L", "75 cl" – a volume means values per 100 ml.
VOLUME_PATTERN = re.compile(r"\d\s*(ml|cl|dl|l|liter|litre)\b", re.IGNORECASE)


@dataclass(frozen=True)
class TrimmedFood:
    barcode: str
    name: str
    brand: str
    basis: str
    kcal: float
    protein: float
    carbs: float
    fat: float
    serving: float | None
    scans: int


COLUMNS = tuple(field.name for field in fields(TrimmedFood))


def _number(value):
    try:
        number = float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return None

    return number if number == number else None  # NaN


def _text(value, max_length):
    return " ".join((value or "").split())[:max_length].strip()


def _kcal(row):
    kcal = _number(row.get("energy-kcal_100g"))

    if kcal is not None:
        return kcal

    # energy_100g is kJ in the export.
    kj = _number(row.get("energy-kj_100g"))

    if kj is None:
        kj = _number(row.get("energy_100g"))

    return kj / KJ_PER_KCAL if kj is not None else None


def _basis(row):
    is_volume = VOLUME_PATTERN.search(row.get("quantity") or "")

    return Basis.MILLILITRE.value if is_volume else Basis.GRAM.value


def _serving(row):
    serving = _number(row.get("serving_quantity"))

    if serving is None or not SERVING_MIN <= serving <= SERVING_MAX:
        return None

    return round(serving, 1)


def trim_row(row, countries=DEFAULT_COUNTRIES):
    """A TrimmedFood for a usable product, None for everything else."""
    barcode = (row.get("code") or "").strip()

    if not BARCODE_PATTERN.match(barcode):
        return None

    tags = set((row.get("countries_tags") or "").split(","))

    if tags.isdisjoint(countries):
        return None

    name = _text(row.get("product_name"), NAME_MAX_LENGTH)

    if not name:
        return None

    kcal = _kcal(row)
    protein = _number(row.get("proteins_100g"))
    carbs = _number(row.get("carbohydrates_100g"))
    fat = _number(row.get("fat_100g"))

    if None in (kcal, protein, carbs, fat):
        return None

    macros = (protein, carbs, fat)

    if not 0 <= kcal <= KCAL_MAX_PER_100:
        return None

    if any(not 0 <= value <= MACRO_MAX_PER_100 for value in macros):
        return None

    if sum(macros) > MACRO_SUM_MAX:
        return None

    return TrimmedFood(
        barcode=barcode,
        name=name,
        brand=_text((row.get("brands") or "").split(",")[0], BRAND_MAX_LENGTH),
        basis=_basis(row),
        kcal=round(kcal, 1),
        protein=round(protein, 1),
        carbs=round(carbs, 1),
        fat=round(fat, 1),
        serving=_serving(row),
        scans=max(int(_number(row.get("unique_scans_n")) or 0), 0),
    )


def open_text(path, mode="rt"):
    """Opens plain or gzipped files, chosen by the file name."""
    if str(path).endswith(".gz"):
        return gzip.open(path, mode, encoding="utf-8", newline="")

    return open(path, mode, encoding="utf-8", newline="")


def read_export(stream):
    """Rows of the raw export as dicts; it uses tabs and no quoting."""
    csv.field_size_limit(sys.maxsize)

    return csv.DictReader(stream, delimiter="\t", quoting=csv.QUOTE_NONE)


def trim_export(rows, countries=DEFAULT_COUNTRIES):
    """Usable products, each barcode once (the first row wins)."""
    seen = set()

    for row in rows:
        food = trim_row(row, countries)

        if food is None or food.barcode in seen:
            continue

        seen.add(food.barcode)

        yield food


def write_trimmed(stream, foods):
    writer = csv.writer(stream)
    writer.writerow(COLUMNS)
    count = 0

    for food in foods:
        writer.writerow("" if value is None else value for value in astuple(food))
        count += 1

    return count


def read_trimmed(stream):
    reader = csv.DictReader(stream)

    if tuple(reader.fieldnames or ()) != COLUMNS:
        raise ValueError(f"Expected the columns {', '.join(COLUMNS)}.")

    for row in reader:
        yield TrimmedFood(
            barcode=row["barcode"],
            name=row["name"],
            brand=row["brand"],
            basis=row["basis"],
            kcal=float(row["kcal"]),
            protein=float(row["protein"]),
            carbs=float(row["carbs"]),
            fat=float(row["fat"]),
            serving=float(row["serving"]) if row["serving"] else None,
            scans=int(row["scans"]),
        )
