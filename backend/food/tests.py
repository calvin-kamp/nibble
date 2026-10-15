import gzip
import shutil
import tempfile
from decimal import Decimal
from io import StringIO
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.test import SimpleTestCase, TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from food.models import Basis, Food, FoodUnit
from food.off import TrimmedFood, trim_export, trim_row


def create_food(name, brand="", barcode=None, popularity=0, basis=Basis.GRAM):
    return Food.objects.create(
        name=name,
        brand=brand,
        barcode=barcode,
        basis=basis,
        popularity=popularity,
        kcal_per_100=Decimal(368),
        protein_per_100=Decimal("13.5"),
        carbs_per_100=Decimal("58.7"),
        fat_per_100=Decimal(7),
    )


def export_row(**overrides):
    """One row of the Open Food Facts export with the columns trim_row reads."""
    row = {
        "code": "4009249001256",
        "product_name": "  Haferflocken   kernig ",
        "brands": "Feldmühle, Mühle AG",
        "countries_tags": "en:france,en:germany",
        "quantity": "500 g",
        "serving_quantity": "40",
        "energy-kcal_100g": "368",
        "energy-kj_100g": "",
        "energy_100g": "",
        "proteins_100g": "13.5",
        "carbohydrates_100g": "58.7",
        "fat_100g": "7.04",
        "unique_scans_n": "812",
    }
    row.update(overrides)

    return row


class FoodApiTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            email="ich@example.com", password="x"
        )

    def setUp(self):
        self.client.force_authenticate(self.user)


class FoodSearchTests(FoodApiTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.oats = create_food("Haferflocken, kernig", brand="Feldmuehle", popularity=5)
        FoodUnit.objects.create(food=cls.oats, kind=FoodUnit.Kind.PORTION, amount=40)
        create_food("Haferflocken, zart", popularity=50)
        create_food("Vollkornbrot mit Hafer", popularity=999)
        create_food("Haferdrink", basis=Basis.MILLILITRE)
        create_food("Banane")

    def search(self, term):
        return self.client.get("/foods/", {"suche": term})

    def test_requires_login(self):
        self.client.force_authenticate(None)

        self.assertIn(self.search("hafer").status_code, (401, 403))

    def test_prefix_matches_first_then_popular_products(self):
        names = [food["name"] for food in self.search("hafer").json()]

        self.assertEqual(
            names,
            [
                "Haferflocken, zart",
                "Haferflocken, kernig",
                "Haferdrink",
                "Vollkornbrot mit Hafer",
            ],
        )

    def test_every_word_must_match_name_or_brand(self):
        names = [food["name"] for food in self.search("hafer  feldmuehle").json()]

        self.assertEqual(names, ["Haferflocken, kernig"])

    def test_hit_has_basis_values_and_units(self):
        hit = self.search("kernig").json()[0]

        self.assertEqual(
            hit,
            {
                "id": self.oats.id,
                "name": "Haferflocken, kernig",
                "brand": "Feldmuehle",
                "basis": "g",
                "per100": {"kcal": 368.0, "protein": 13.5, "carbs": 58.7, "fat": 7.0},
                "units": [
                    {"key": "g", "name": "g", "amount": 1.0},
                    {"key": "portion", "name": "Portion", "amount": 40.0},
                ],
            },
        )

    def test_drinks_are_measured_in_millilitres(self):
        hit = self.search("haferdrink").json()[0]

        self.assertEqual(hit["basis"], "ml")
        self.assertEqual(hit["units"][0]["key"], "ml")

    def test_term_needs_two_characters(self):
        response = self.search(" h ")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("suche", response.json())

    def test_returns_at_most_20_hits(self):
        for number in range(25):
            create_food(f"Apfel {number}")

        self.assertEqual(len(self.search("apfel").json()), 20)


class FoodLookupTests(FoodApiTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.ean = create_food("Haferflocken", barcode="4009249001256")
        cls.upc = create_food("Cornflakes", barcode="038000138416")

    def test_detail(self):
        response = self.client.get(f"/foods/{self.ean.id}/")

        self.assertEqual(response.json()["name"], "Haferflocken")

    def test_finds_by_barcode(self):
        response = self.client.get("/foods/barcode/4009249001256/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], self.ean.id)

    def test_upc_a_and_ean_13_with_leading_zero_are_the_same_product(self):
        response = self.client.get("/foods/barcode/0038000138416/")

        self.assertEqual(response.json()["id"], self.upc.id)

    def test_unknown_barcode_is_not_found(self):
        response = self.client.get("/foods/barcode/4000000000000/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TrimRowTests(SimpleTestCase):
    def test_keeps_the_needed_columns_cleaned_up(self):
        self.assertEqual(
            trim_row(export_row()),
            TrimmedFood(
                barcode="4009249001256",
                name="Haferflocken kernig",
                brand="Feldmühle",
                basis="g",
                kcal=368.0,
                protein=13.5,
                carbs=58.7,
                fat=7.0,
                serving=40.0,
                scans=812,
            ),
        )

    def test_volume_packs_are_measured_in_millilitres(self):
        for quantity in ("1 l", "330ml", "6 x 0,33 L", "75 cl"):
            with self.subTest(quantity):
                self.assertEqual(trim_row(export_row(quantity=quantity)).basis, "ml")

    def test_falls_back_to_kilojoules(self):
        food = trim_row(export_row(**{"energy-kcal_100g": "", "energy_100g": "1540"}))

        self.assertEqual(food.kcal, 368.1)

    def test_implausible_portions_are_dropped(self):
        for serving in ("", "0", "5000", "abc"):
            with self.subTest(serving):
                self.assertIsNone(
                    trim_row(export_row(serving_quantity=serving)).serving
                )

    def test_skips_unusable_products(self):
        cases = {
            "other country": {"countries_tags": "en:france"},
            "internal code": {"code": "2001234"},
            "no name": {"product_name": "   "},
            "no fat": {"fat_100g": ""},
            "no energy": {"energy-kcal_100g": ""},
            "too much energy": {"energy-kcal_100g": "1200"},
            "negative": {"proteins_100g": "-1"},
            "macros over 100 g": {"carbohydrates_100g": "90", "fat_100g": "20"},
        }

        for case, overrides in cases.items():
            with self.subTest(case):
                self.assertIsNone(trim_row(export_row(**overrides)))

    def test_export_keeps_each_barcode_once(self):
        rows = [
            export_row(),
            export_row(product_name="Doppelt"),
            export_row(code="12345678"),
        ]

        self.assertEqual(
            [food.barcode for food in trim_export(rows)],
            ["4009249001256", "12345678"],
        )


class TrimAndImportCommandTests(TestCase):
    def setUp(self):
        self.directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.directory)

    def write_export(self, rows):
        path = self.directory / "export.csv.gz"
        columns = list(export_row())

        with gzip.open(path, "wt", encoding="utf-8", newline="") as stream:
            stream.write("\t".join(columns) + "\n")

            for row in rows:
                stream.write("\t".join(row[column] for column in columns) + "\n")

        return path

    def trim_and_import(self, rows):
        target = self.directory / "trimmed.csv.gz"
        call_command(
            "trim_off_dump",
            str(self.write_export(rows)),
            str(target),
            stdout=StringIO(),
        )
        call_command("import_foods", str(target), stdout=StringIO())

    def test_imports_and_updates_by_barcode(self):
        self.trim_and_import(
            [export_row(), export_row(code="12345678", countries_tags="en:france")]
        )
        Food.objects.update(name="Alt")
        self.trim_and_import([export_row(serving_quantity="50")])

        food = Food.objects.get()
        self.assertEqual(
            (food.barcode, food.name, food.brand, food.popularity, food.source),
            ("4009249001256", "Haferflocken kernig", "Feldmühle", 812, "off"),
        )
        self.assertEqual(
            list(food.units.values_list("kind", "amount")),
            [("portion", Decimal("50.0"))],
        )

    def test_portion_disappears_when_the_export_drops_it(self):
        self.trim_and_import([export_row()])
        self.trim_and_import([export_row(serving_quantity="")])

        self.assertFalse(FoodUnit.objects.exists())

    def test_import_rejects_other_files(self):
        path = self.directory / "other.csv"
        path.write_text("a,b\n1,2\n", encoding="utf-8")

        with self.assertRaises(CommandError):
            call_command("import_foods", str(path), stdout=StringIO())


class SeedFoodsTests(TestCase):
    def test_creates_basic_foods_with_household_measures_and_can_run_twice(self):
        call_command("seed_foods", stdout=StringIO())
        count = Food.objects.count()
        call_command("seed_foods", stdout=StringIO())

        bread = Food.objects.get(name="Toastbrot")
        self.assertEqual(Food.objects.count(), count)
        self.assertEqual(
            list(bread.units.values_list("kind", "amount")),
            [("slice", Decimal("25.0"))],
        )
