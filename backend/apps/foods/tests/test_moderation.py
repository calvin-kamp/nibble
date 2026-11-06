import json
from unittest import mock
from urllib.error import URLError

from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.foods.models import FoodProduct, FoodReport, MissingBarcode
from apps.foods.utils import clean_product_name, has_valid_check_digit, repair_mojibake
from config.testing import ApiTestCase

CODE = "4065002004209"


def product_input(**overrides):
    data = {
        "name": "Geflügel-Wiener",
        "brand": "Güldenhof",
        "base_unit": "g",
        "package_quantity": 500,
        "serving_quantity": 50,
        "countries": ["en:germany", "en:austria"],
        "nutrition_per_100": {
            "kj": 1003,
            "kcal": 242,
            "fat": 20,
            "saturated_fat": 7.1,
            "carbs": 1,
            "sugars": 0.5,
            "protein": 14,
            "salt": 2.1,
        },
    }
    data.update(overrides)

    return data


class FakeResponse:
    def __init__(self, data):
        self.body = json.dumps(data).encode()

    def read(self, *args):
        body, self.body = self.body, b""

        return body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


@override_settings(
    OFF_API_URL="https://off.test",
    OFF_API_BASIC_AUTH="",
    OFF_USER_ID="nibble-app",
    OFF_PASSWORD="geheim",
)
class MissingBarcodeModerationTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.staff = self.create_user("staff@example.com", is_staff=True)
        self.login(self.staff)
        MissingBarcode.objects.create(code=CODE, lookups=3)
        MissingBarcode.objects.create(code="4000000000017", lookups=8)

    def detail_url(self, code=CODE):
        return reverse("missing_barcode-detail", args=[code])

    def product_url(self, code=CODE):
        return reverse("missing_barcode-product", args=[code])

    def test_staff_only(self):
        self.login(self.create_user())

        response = self.client.get(reverse("missing_barcode-list"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_most_searched_first(self):
        response = self.client.get(reverse("missing_barcode-list"))

        self.assertEqual(
            [item["code"] for item in response.data["results"]], ["4000000000017", CODE]
        )
        self.assertEqual(response.data["results"][0]["lookups"], 8)

    @mock.patch("urllib.request.urlopen")
    def test_detail_prefills_from_off(self, urlopen):
        urlopen.return_value = FakeResponse(
            {
                "status": 1,
                "product": {
                    "product_name": "GÃ¼ldenhof GeflÃ¼gel-Wiener",
                    "brands": "Aldi, Güldenhof",
                    "product_quantity": "500",
                    "product_quantity_unit": "g",
                    "countries_tags": ["en:germany", "en:france"],
                    "nutriments": {"energy-kcal_100g": 242},
                },
            }
        )

        data = self.client.get(self.detail_url()).data
        prefill = data["off_product"]

        self.assertEqual(data["lookups"], 3)
        self.assertEqual(prefill["name"], "Güldenhof Geflügel-Wiener")
        self.assertEqual(prefill["brand"], "Aldi")
        self.assertEqual(prefill["package_quantity"], 500)
        self.assertEqual(prefill["countries"], ["en:germany"])
        self.assertEqual(prefill["nutrition_per_100"]["kcal"], 242)
        self.assertIsNone(prefill["nutrition_per_100"]["fat"])
        request = urlopen.call_args.args[0]
        self.assertTrue(request.full_url.startswith(f"https://off.test/api/v2/product/{CODE}"))
        self.assertIn("nibble/1.0", request.get_header("User-agent"))

    @mock.patch("urllib.request.urlopen", side_effect=URLError("offline"))
    def test_detail_without_off(self, urlopen):
        response = self.client.get(self.detail_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["off_product"])

    @mock.patch("urllib.request.urlopen")
    def test_add_product_saves_on_off_and_here(self, urlopen):
        urlopen.return_value = FakeResponse({"status": 1, "status_verbose": "fields saved"})

        response = self.client.post(self.product_url(), product_input(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["off_synced"])
        self.assertEqual(response.data["product"]["nutrition_per_100"]["kcal"], 242.0)

        product = FoodProduct.objects.get(code=CODE)
        self.assertEqual(product.name, "Geflügel-Wiener")
        self.assertEqual(product.brand, "Güldenhof")
        self.assertEqual(product.package_quantity, 500)
        self.assertEqual(product.fat_per_100, 20)
        self.assertIsNotNone(product.curated_at)
        self.assertFalse(MissingBarcode.objects.filter(code=CODE).exists())

        request = urlopen.call_args.args[0]
        sent = dict(item.split("=", 1) for item in request.data.decode().split("&"))
        self.assertEqual(request.full_url, "https://off.test/cgi/product_jqm2.pl")
        self.assertEqual(sent["code"], CODE)
        self.assertEqual(sent["user_id"], "nibble-app")
        self.assertEqual(sent["quantity"], "500+g")
        self.assertEqual(sent["countries"], "en%3Agermany%2Cen%3Aaustria")
        self.assertEqual(sent["nutriment_saturated-fat"], "7.1")
        self.assertEqual(sent["nutriment_salt"], "2.1")
        self.assertEqual(sent["nutriment_energy-kj"], "1003")
        self.assertNotIn("nutriment_fiber", sent)

    @mock.patch("urllib.request.urlopen", side_effect=URLError("offline"))
    def test_nothing_saved_when_off_fails(self, urlopen):
        response = self.client.post(self.product_url(), product_input(), format="json")

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(response.data["code"], "off_unavailable")
        self.assertFalse(FoodProduct.objects.filter(code=CODE).exists())
        self.assertTrue(MissingBarcode.objects.filter(code=CODE).exists())

    @mock.patch("urllib.request.urlopen")
    def test_off_refusal_counts_as_failure(self, urlopen):
        urlopen.return_value = FakeResponse({"status": 0, "status_verbose": "no code"})

        response = self.client.post(self.product_url(), product_input(), format="json")

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertFalse(FoodProduct.objects.filter(code=CODE).exists())

    @override_settings(OFF_USER_ID="")
    @mock.patch("urllib.request.urlopen")
    def test_without_off_account_only_saved_here(self, urlopen):
        response = self.client.post(self.product_url(), product_input(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data["off_synced"])
        self.assertTrue(FoodProduct.objects.filter(code=CODE).exists())
        urlopen.assert_not_called()

    @mock.patch("urllib.request.urlopen")
    def test_validates_nutrition(self, urlopen):
        nutrition = {
            **product_input()["nutrition_per_100"],
            "saturated_fat": 30,
            "sugars": 2,
            "kcal": 950,
        }
        response = self.client.post(
            self.product_url(),
            product_input(nutrition_per_100=nutrition, countries=[]),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            set(response.data["errors"]),
            {"countries", "nutrition_per_100.kcal"},
        )
        urlopen.assert_not_called()

        nutrition["kcal"] = 242
        response = self.client.post(
            self.product_url(), product_input(nutrition_per_100=nutrition), format="json"
        )
        self.assertEqual(
            set(response.data["errors"]),
            {"nutrition_per_100.saturated_fat", "nutrition_per_100.sugars"},
        )

    @mock.patch("urllib.request.urlopen")
    def test_conflict_when_product_exists(self, urlopen):
        FoodProduct.objects.create(
            code=CODE,
            name="Inzwischen importiert",
            kcal_per_100=1,
            protein_per_100=1,
            carbs_per_100=1,
            fat_per_100=1,
            imported_at=timezone.now(),
        )

        response = self.client.post(self.product_url(), product_input(), format="json")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["code"], "product_exists")
        self.assertFalse(MissingBarcode.objects.filter(code=CODE).exists())
        urlopen.assert_not_called()

    def test_dismiss(self):
        response = self.client.delete(self.detail_url())

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(MissingBarcode.objects.filter(code=CODE).exists())


def create_product(code=CODE, **overrides):
    values = {
        "name": "Proteindrink Vanille",
        "brand": "yfood",
        "base_unit": "g",
        "kcal_per_100": 60,
        "protein_per_100": 6,
        "carbs_per_100": 5,
        "fat_per_100": 1.5,
        "imported_at": timezone.now(),
        **overrides,
    }

    return FoodProduct.objects.create(code=code, **values)


def correction(**overrides):
    return {
        "name": "Proteindrink Vanille",
        "brand": "yfood",
        "base_unit": "ml",
        "package_quantity": 500,
        "serving_quantity": None,
        "nutrition_per_100": {"kcal": 64, "protein": 6.6, "carbs": 5.2, "fat": 1.6},
        **overrides,
    }


def sent_fields(urlopen):
    body = urlopen.call_args.args[0].data.decode()

    return dict(item.split("=", 1) for item in body.split("&"))


class FoodReportTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.login(self.create_user())
        self.product = create_product()

    def test_report_without_reporter(self):
        response = self.client.post(
            reverse("food_report", args=[CODE]),
            {"reason": "unit", "comment": " Ist ein Getränk "},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        report = FoodReport.objects.get()
        self.assertEqual(report.reason, "unit")
        self.assertEqual(report.comment, "Ist ein Getränk")
        self.assertEqual(
            {field.name for field in FoodReport._meta.fields},
            {"id", "product", "reason", "comment", "created_at"},
        )

    def test_unknown_product_and_reason(self):
        missing = self.client.post(
            reverse("food_report", args=["4000000000017"]), {"reason": "unit"}, format="json"
        )
        invalid = self.client.post(
            reverse("food_report", args=[CODE]), {"reason": "egal"}, format="json"
        )

        self.assertEqual(missing.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)


@override_settings(
    OFF_API_URL="https://off.test",
    OFF_API_BASIC_AUTH="",
    OFF_USER_ID="nibble-app",
    OFF_PASSWORD="geheim",
)
class FoodModerationTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.login(self.create_user("staff@example.com", is_staff=True))
        self.product = create_product()

    def test_staff_only(self):
        self.login(self.create_user())

        response = self.client.get(reverse("moderation_food-reported"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reported_most_reported_first(self):
        other = create_product("4000000000017", name="Skyr")
        FoodReport.objects.create(product=self.product, reason="unit")
        FoodReport.objects.create(product=other, reason="nutrition")
        FoodReport.objects.create(product=other, reason="name")

        results = self.client.get(reverse("moderation_food-reported")).data["results"]

        self.assertEqual([item["code"] for item in results], ["4000000000017", CODE])
        self.assertEqual(results[0]["report_count"], 2)
        self.assertEqual(results[0]["reasons"], ["name", "nutrition"])

    def test_detail_with_reports(self):
        FoodReport.objects.create(product=self.product, reason="unit", comment="Getränk")

        data = self.client.get(reverse("moderation_food-detail", args=[CODE])).data

        self.assertEqual(data["nutrition_per_100"]["kcal"], 60)
        self.assertEqual(data["reports"][0]["comment"], "Getränk")

    @mock.patch("urllib.request.urlopen")
    def test_correction_sends_values_but_not_the_name(self, urlopen):
        urlopen.return_value = FakeResponse({"status": 1})
        FoodReport.objects.create(product=self.product, reason="unit")

        response = self.client.put(
            reverse("moderation_food-detail", args=[CODE]),
            correction(name="Vanille Proteindrink"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["off_synced"])
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Vanille Proteindrink")
        self.assertEqual(self.product.base_unit, "ml")
        self.assertIsNotNone(self.product.curated_at)
        self.assertFalse(FoodReport.objects.exists())

        sent = sent_fields(urlopen)
        self.assertEqual(sent["quantity"], "500+ml")
        self.assertEqual(sent["nutriment_energy-kcal"], "64")
        self.assertNotIn("product_name", sent)
        self.assertNotIn("brands", sent)
        self.assertNotIn("countries", sent)

    @mock.patch("urllib.request.urlopen", side_effect=URLError("offline"))
    def test_correction_not_saved_when_off_fails(self, urlopen):
        response = self.client.put(
            reverse("moderation_food-detail", args=[CODE]), correction(), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.product.refresh_from_db()
        self.assertEqual(self.product.base_unit, "g")

    def test_dismiss_reports(self):
        FoodReport.objects.create(product=self.product, reason="unit")

        response = self.client.delete(reverse("moderation_food-reports", args=[CODE]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FoodReport.objects.exists())
        self.assertTrue(FoodProduct.objects.filter(code=CODE).exists())

    @mock.patch("urllib.request.urlopen")
    def test_generic_food_stays_in_nibble(self, urlopen):
        response = self.client.post(
            reverse("moderation_food-generic"),
            correction(name="Feige", brand="", base_unit="g", package_quantity=None),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product = FoodProduct.objects.get(name="Feige")
        self.assertTrue(product.generic)
        self.assertTrue(product.code.startswith("n"))
        self.assertIsNotNone(product.curated_at)

        # Corrections of generic foods don't go to OFF either.
        response = self.client.put(
            reverse("moderation_food-detail", args=[product.code]),
            correction(name="Feige frisch", base_unit="g"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(product.name, "Feige frisch")
        urlopen.assert_not_called()

    def test_generic_first_in_search(self):
        create_product("4000000000017", name="Bananenchips")

        response = self.client.get(reverse("food_search"), {"q": "banane"})

        self.assertEqual(response.data["results"][0]["name"], "Banane")
        self.assertTrue(response.data["results"][0]["generic"])

        # Recent foods find a generic food by its code, it has no barcode.
        code = response.data["results"][0]["code"]
        by_code = self.client.get(reverse("food_search"), {"code": code}).data

        self.assertEqual([item["name"] for item in by_code["results"]], ["Banane"])


class BarcodeUtilsTests(ApiTestCase):
    def test_check_digit(self):
        self.assertTrue(has_valid_check_digit("4065002004209"))
        self.assertTrue(has_valid_check_digit("4255719323476"))
        self.assertTrue(has_valid_check_digit("96385074"))
        self.assertFalse(has_valid_check_digit("4065002004208"))
        self.assertFalse(has_valid_check_digit("12345"))

    def test_repair_mojibake(self):
        self.assertEqual(repair_mojibake("GÃ¼ldenhof"), "Güldenhof")
        self.assertEqual(repair_mojibake("Güldenhof"), "Güldenhof")

    def test_clean_product_name(self):
        self.assertEqual(
            clean_product_name(
                "ALDI GÜLDENHOF HUHN Hähnchenbrustfilet 150g 2.29€ 1kg 15.27€", "Aldi"
            ),
            "Güldenhof Huhn Hähnchenbrustfilet",
        )
        self.assertEqual(clean_product_name("Protein Drink Vanilla 500ml"), "Protein Drink Vanilla")
        self.assertEqual(clean_product_name("Coca-Cola 6 x 0,33 l"), "Coca-Cola")
        self.assertEqual(clean_product_name("Vollmilch 3,5% 1l"), "Vollmilch 3,5%")
        self.assertEqual(clean_product_name("BIO Haferflocken"), "BIO Haferflocken")
        self.assertEqual(clean_product_name("NUTELLA"), "NUTELLA")
        self.assertEqual(clean_product_name("500g"), "500g")
