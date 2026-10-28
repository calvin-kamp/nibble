import gzip
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.utils import timezone
from rest_framework import status

from config.testing import ApiTestCase
from foods.models import FoodProduct

# A few columns of the export besides the ones the import reads, as in the real file
EXPORT_COLUMNS = (
    "code",
    "url",
    "product_name",
    "quantity",
    "brands",
    "countries_tags",
    "serving_size",
    "serving_quantity",
    "product_quantity",
    "popularity_tags",
    "energy-kcal_100g",
    "fat_100g",
    "carbohydrates_100g",
    "proteins_100g",
)


def export_line(code, **overrides):
    year = timezone.now().year
    product = {
        "code": code,
        "url": f"https://world.openfoodfacts.org/product/{code}",
        "product_name": "Haferflocken",
        "quantity": "500 g",
        "brands": "Kölln, Peter Kölln KGaA",
        "countries_tags": "en:germany,en:austria",
        "serving_size": "40 g",
        "serving_quantity": "40",
        "product_quantity": "500",
        "popularity_tags": f"top-75-percent-scans-{year - 1},top-de-scans-{year - 1}",
        "energy-kcal_100g": "372",
        "fat_100g": "7",
        "carbohydrates_100g": "58.7",
        "proteins_100g": "13.5",
    }
    product.update(overrides)

    return "\t".join(product[column] for column in EXPORT_COLUMNS)


class FoodSearchTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.login(self.create_user())
        FoodProduct.objects.create(
            code="4000000000001",
            name="Haferflocken zart",
            brand="Kölln",
            kcal_per_100=372,
            protein_per_100=13.5,
            carbs_per_100=58.7,
            fat_per_100=7,
            imported_at=timezone.now(),
        )

    def test_search_by_text_and_barcode(self):
        by_text = self.client.get("/foods/search", {"q": "HAFER"}).json()
        by_brand = self.client.get("/foods/search", {"q": "kölln"}).json()
        by_code = self.client.get("/foods/search", {"barcode": "4000000000001"})

        self.assertEqual(by_text["count"], 1)
        self.assertEqual(by_text["results"][0]["nutrition_per_100"]["kcal"], 372.0)
        self.assertEqual(by_brand["count"], 1)
        self.assertEqual(by_code.json()["results"][0]["name"], "Haferflocken zart")

    def test_every_word_matches_name_or_brand(self):
        def count(query):
            return self.client.get("/foods/search", {"q": query}).json()["count"]

        self.assertEqual(count("kölln zart"), 1)
        self.assertEqual(count("zart  HAFER"), 1)
        self.assertEqual(count("kölln dinkel"), 0)

    def test_barcode_with_spaces_or_hyphens(self):
        def names(params):
            response = self.client.get("/foods/search", params)

            return [product["name"] for product in response.json()["results"]]

        self.assertEqual(names({"barcode": "4 000000 000001"}), ["Haferflocken zart"])
        self.assertEqual(names({"barcode": "4000-0000-00001"}), ["Haferflocken zart"])
        self.assertEqual(names({"q": "4 000000 000001"}), ["Haferflocken zart"])

        invalid = self.client.get("/foods/search", {"barcode": "12 34"})
        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("barcode", invalid.json()["errors"])

    def test_search_needs_q_or_barcode(self):
        empty = self.client.get("/foods/search")
        short = self.client.get("/foods/search", {"q": "h"})

        self.assertEqual(empty.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("q", empty.json()["errors"])
        self.assertIn("q", short.json()["errors"])


class ImportCommandTests(ApiTestCase):
    def import_lines(self, *lines, **options):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.csv.gz"

            with gzip.open(path, "wt", encoding="utf-8") as export:
                export.write("\n".join(["\t".join(EXPORT_COLUMNS), *lines]))

            call_command("import_off_products", source=str(path), stdout=StringIO(), **options)

    def codes(self):
        return sorted(FoodProduct.objects.values_list("code", flat=True))

    def test_imports_only_complete_and_plausible_products(self):
        FoodProduct.objects.create(
            code="99999999",
            name="Veraltet",
            kcal_per_100=1,
            protein_per_100=1,
            carbs_per_100=1,
            fat_per_100=1,
            imported_at=timezone.now(),
        )

        self.import_lines(
            export_line("4000000000001"),
            export_line("4000000000002", product_name="Hafermilch", quantity="1 l", serving_quantity=""),
            export_line("4000000000003", countries_tags="en:france"),
            export_line("4000000000004", product_name=""),
            export_line("4000000000005", **{"fat_100g": ""}),
            export_line(
                "4000000000006",
                **{"energy-kcal_100g": "500", "proteins_100g": "80", "carbohydrates_100g": "80"},
            ),
            export_line("12345"),
            "kaputte Zeile en:germany",
        )

        oats = FoodProduct.objects.get(code="4000000000001")
        drink = FoodProduct.objects.get(code="4000000000002")
        self.assertEqual(self.codes(), ["4000000000001", "4000000000002"])
        self.assertEqual(oats.name, "Haferflocken")
        self.assertEqual(oats.brand, "Kölln")
        self.assertEqual(oats.base_unit, "g")
        self.assertEqual(oats.serving_quantity, 40)
        self.assertEqual(oats.package_quantity, 500)
        self.assertEqual(oats.kcal_per_100, 372)
        self.assertEqual(drink.base_unit, "ml")
        self.assertIsNone(drink.serving_quantity)

    def test_skips_products_without_recent_scans(self):
        year = timezone.now().year

        self.import_lines(
            export_line("4000000000011", popularity_tags=f"top-75-percent-scans-{year}"),
            export_line("4000000000012", popularity_tags=f"top-de-scans-{year - 2}"),
            export_line("4000000000013", popularity_tags=f"top-de-scans-{year - 3}"),
            export_line("4000000000014", popularity_tags=""),
        )

        self.assertEqual(self.codes(), ["4000000000011", "4000000000012"])

    def test_scan_years_zero_imports_all(self):
        self.import_lines(
            export_line("4000000000021", popularity_tags="top-de-scans-2015"),
            export_line("4000000000022", popularity_tags=""),
            scan_years=0,
        )

        self.assertEqual(self.codes(), ["4000000000021", "4000000000022"])

    def test_limit_keeps_products_it_did_not_reach(self):
        FoodProduct.objects.create(
            code="99999999",
            name="Bleibt",
            kcal_per_100=1,
            protein_per_100=1,
            carbs_per_100=1,
            fat_per_100=1,
            imported_at=timezone.now(),
        )

        self.import_lines(export_line("4000000000031"), export_line("4000000000032"), limit=1)

        self.assertIn("99999999", self.codes())
        self.assertEqual(FoodProduct.objects.count(), 2)
