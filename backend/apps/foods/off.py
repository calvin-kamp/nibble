"""Talks to the Open Food Facts API: reads a product, writes the ones staff add.

Docs: https://openfoodfacts.github.io/openfoodfacts-server/api/
Product reads are limited to 15 per minute and IP, so only staff call this.
"""

import base64
import hashlib
import json
import logging
import urllib.error
import urllib.parse
import urllib.request
import uuid

from django.conf import settings

from apps.foods.utils import clean_product_name, repair_mojibake

logger = logging.getLogger(__name__)

READ_FIELDS = (
    "product_name",
    "product_name_de",
    "brands",
    "product_quantity",
    "product_quantity_unit",
    "serving_quantity",
    "countries_tags",
    "nutriments",
)

# Fields of the admin form -> nutriment names of OFF, all per 100 g/ml.
NUTRIMENTS = {
    "kj": ("energy-kj", "kJ"),
    "kcal": ("energy-kcal", "kcal"),
    "fat": ("fat", "g"),
    "saturated_fat": ("saturated-fat", "g"),
    "carbs": ("carbohydrates", "g"),
    "sugars": ("sugars", "g"),
    "fiber": ("fiber", "g"),
    "protein": ("proteins", "g"),
    "salt": ("salt", "g"),
}


class OffError(Exception):
    """Open Food Facts did not accept the product or could not be reached."""


def is_write_configured():
    return bool(settings.OFF_USER_ID and settings.OFF_PASSWORD)


def request(path, data=None):
    headers = {"User-Agent": settings.OFF_USER_AGENT}

    if settings.OFF_API_BASIC_AUTH:
        token = base64.b64encode(settings.OFF_API_BASIC_AUTH.encode()).decode()
        headers["Authorization"] = f"Basic {token}"

    body = urllib.parse.urlencode(data).encode() if data is not None else None
    req = urllib.request.Request(f"{settings.OFF_API_URL}{path}", data=body, headers=headers)

    with urllib.request.urlopen(req, timeout=settings.OFF_API_TIMEOUT) as response:
        return json.load(response)


def fetch_product(code):
    """What OFF knows about a barcode, to prefill the form. None if nothing or offline."""
    query = urllib.parse.urlencode({"fields": ",".join(READ_FIELDS)})

    try:
        data = request(f"/api/v2/product/{code}.json?{query}")
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            logger.warning("OFF read for %s failed: %s", code, exc)

        return None
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        logger.warning("OFF read for %s failed: %s", code, exc)

        return None

    product = data.get("product") if data.get("status") == 1 else None

    if not product:
        return None

    nutriments = product.get("nutriments") or {}
    unit = (product.get("product_quantity_unit") or "g").lower()
    name = repair_mojibake((product.get("product_name_de") or product.get("product_name") or "").strip())
    brand = repair_mojibake((product.get("brands") or "").split(",")[0].strip()) or None

    return {
        "name": clean_product_name(name, brand) or None,
        "brand": brand,
        "base_unit": "ml" if unit == "ml" else "g",
        "package_quantity": number(product.get("product_quantity")),
        "serving_quantity": number(product.get("serving_quantity")),
        "countries": [
            tag
            for tag in product.get("countries_tags") or []
            if tag in ("en:germany", "en:austria", "en:switzerland")
        ],
        "nutrition_per_100": {
            field: number(nutriments.get(f"{nutrient}_100g"))
            for field, (nutrient, _unit) in NUTRIMENTS.items()
        },
    }


def number(value):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None

    return result if result >= 0 else None


def app_uuid(profile):
    """Stable, salted id per staff account, so OFF moderators can tell them apart."""
    digest = hashlib.sha256(f"{settings.SECRET_KEY}:off:{profile.pk}".encode()).digest()

    return str(uuid.UUID(bytes=digest[:16]))


def format_amount(value, unit):
    return f"{value.normalize():f} {unit}"


def save_product(data, profile, with_name=True):
    """Creates or completes the product on OFF. Raises OffError if that fails.

    A correction leaves out name and brand: nibble shortens names for its own search, OFF
    keeps the full one from the packaging.
    """
    unit = data["base_unit"]
    fields = {
        "code": data["code"],
        "user_id": settings.OFF_USER_ID,
        "password": settings.OFF_PASSWORD,
        "app_name": "nibble",
        "app_version": "1.0",
        "app_uuid": app_uuid(profile),
        "comment": "Added in nibble (nibble-tracking.de)",
        "lc": "de",
        "lang": "de",
        "nutrition_data": "on",
        # OFF keeps drinks per 100 g as well and shows them as per 100 ml.
        "nutrition_data_per": "100g",
    }

    if with_name:
        fields["product_name"] = data["name"]
        fields["product_name_de"] = data["name"]

        if data.get("brand"):
            fields["brands"] = data["brand"]

    if data.get("countries"):
        fields["countries"] = ",".join(data["countries"])

    if data.get("package_quantity"):
        fields["quantity"] = format_amount(data["package_quantity"], unit)

    if data.get("serving_quantity"):
        fields["serving_size"] = format_amount(data["serving_quantity"], unit)

    for field, (nutrient, nutrient_unit) in NUTRIMENTS.items():
        value = data["nutrition_per_100"].get(field)

        if value is not None:
            fields[f"nutriment_{nutrient}"] = f"{value.normalize():f}"
            fields[f"nutriment_{nutrient}_unit"] = nutrient_unit

    try:
        result = request("/cgi/product_jqm2.pl", fields)
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        logger.warning("OFF write for %s failed: %s", data["code"], exc)

        raise OffError(str(exc)) from exc

    if result.get("status") != 1:
        logger.warning("OFF refused %s: %s", data["code"], result)

        raise OffError(result.get("status_verbose") or "refused")
