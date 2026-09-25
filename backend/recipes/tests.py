import shutil
import tempfile
from io import BytesIO, StringIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import override_settings
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from recipes.models import Ingredient, Recipe

MEDIA_ROOT = tempfile.mkdtemp()


def recipe_payload(**overrides):
    """Valid camelCase body as the frontend sends it."""
    payload = {
        "name": "Rote Linsensuppe",
        "description": "Cremig und schnell.",
        "servings": 4,
        "durationMinutes": 35,
        "mealTypes": ["Mittagessen"],
        "equipment": ["Herd", "Mixer"],
        "diets": ["Vegan"],
        "intolerances": ["Glutenfrei"],
        "attributes": ["Unter 30 Min"],
        "ingredients": [
            {"name": "Rote Linsen", "amount": 250, "unit": "g"},
            {"name": "Zwiebel", "amount": 1, "unit": "Stück"},
        ],
        "cookingSteps": [{"text": "Zwiebel würfeln."}, {"text": "Alles kochen."}],
        "proteinPerServing": 16,
        "carbsPerServing": 34.5,
        "fatPerServing": 14,
    }
    payload.update(overrides)

    return payload


def image_file(name="bild.png", image_format="PNG"):
    buffer = BytesIO()
    Image.new("RGB", (8, 8), "orange").save(buffer, image_format)

    return SimpleUploadedFile(
        name, buffer.getvalue(), content_type=f"image/{image_format.lower()}"
    )


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RecipeApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed", stdout=StringIO())
        user_model = get_user_model()
        cls.owner = user_model.objects.create_user(
            **{user_model.USERNAME_FIELD: "owner@example.com"}, password="x"
        )
        cls.other = user_model.objects.create_user(
            **{user_model.USERNAME_FIELD: "other@example.com"}, password="x"
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def create_recipe(self, **overrides):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            "/recipes/", recipe_payload(**overrides), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        return response.json()

    def test_create_returns_labels_numbers_and_calculated_kcal(self):
        data = self.create_recipe()

        self.assertEqual(data["kcalPerServing"], round(16 * 4 + 34.5 * 4 + 14 * 9))
        self.assertEqual(data["carbsPerServing"], 34.5)
        self.assertEqual(data["mealTypes"], ["Mittagessen"])
        self.assertEqual(data["attributes"], ["Unter 30 Min"])
        self.assertEqual(
            data["ingredients"][1], {"name": "Zwiebel", "amount": 1.0, "unit": "Stück"}
        )
        self.assertEqual([step["step"] for step in data["cookingSteps"]], [1, 2])
        self.assertTrue(data["isOwner"])
        self.assertTrue(data["slug"].endswith("-rote-linsensuppe"))

    def test_create_requires_login(self):
        response = self.client.post("/recipes/", recipe_payload(), format="json")

        self.assertIn(response.status_code, (401, 403))

    def test_create_rejects_empty_lists_and_unknown_labels(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            "/recipes/",
            recipe_payload(ingredients=[], cookingSteps=[], diets=["Keto"]),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.json()
        self.assertIn("ingredients", errors)
        self.assertIn("cookingSteps", errors)
        self.assertIn("diets", errors)

    def test_ingredients_are_shared_case_insensitively(self):
        self.create_recipe()
        self.create_recipe(
            ingredients=[{"name": "zwiebel", "amount": 2, "unit": "Stück"}]
        )

        self.assertEqual(Ingredient.objects.filter(name__iexact="zwiebel").count(), 1)

    def test_owner_can_replace_everything(self):
        recipe = self.create_recipe()

        response = self.client.put(
            f"/recipes/{recipe['id']}/",
            recipe_payload(
                name="Linsensuppe",
                ingredients=[{"name": "Linsen", "amount": 0.5, "unit": "kg"}],
                cookingSteps=[{"text": "Kochen."}],
                diets=[],
                fatPerServing=0,
            ),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(
            response.json()["ingredients"],
            [{"name": "Linsen", "amount": 0.5, "unit": "kg"}],
        )
        self.assertEqual(
            response.json()["cookingSteps"], [{"step": 1, "text": "Kochen."}]
        )
        self.assertEqual(response.json()["diets"], [])
        self.assertEqual(response.json()["kcalPerServing"], round(16 * 4 + 34.5 * 4))

    def test_others_can_read_but_not_change(self):
        recipe = self.create_recipe()
        self.client.force_authenticate(self.other)

        detail = self.client.get(f"/recipes/{recipe['id']}/")
        update = self.client.put(
            f"/recipes/{recipe['id']}/", recipe_payload(), format="json"
        )
        delete = self.client.delete(f"/recipes/{recipe['id']}/")

        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertFalse(detail.json()["isOwner"])
        self.assertEqual(update.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_contains_slug_and_no_detail_fields(self):
        self.create_recipe()
        self.client.force_authenticate(None)

        item = self.client.get("/recipes/").json()[0]

        self.assertIn("slug", item)
        self.assertNotIn("ingredients", item)

    def test_image_upload_replace_and_delete(self):
        recipe = self.create_recipe()
        url = f"/recipes/{recipe['id']}/image/"

        first = self.client.put(url, {"image": image_file()}, format="multipart")
        first_name = Recipe.objects.get(pk=recipe["id"]).image.name
        second = self.client.put(
            url, {"image": image_file("b.jpg", "JPEG")}, format="multipart"
        )
        storage = Recipe.objects.get(pk=recipe["id"]).image.storage

        self.assertEqual(first.status_code, status.HTTP_200_OK, first.data)
        self.assertTrue(first.json()["image"].startswith("http"))
        self.assertEqual(second.status_code, status.HTTP_200_OK, second.data)
        self.assertFalse(storage.exists(first_name))

        removed = self.client.delete(url)

        self.assertEqual(removed.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.get(pk=recipe["id"]).image)

    def test_image_rejects_wrong_format(self):
        recipe = self.create_recipe()

        response = self.client.put(
            f"/recipes/{recipe['id']}/image/",
            {"image": image_file("bild.gif", "GIF")},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("image", response.json())

    def test_image_only_for_owner(self):
        recipe = self.create_recipe()
        self.client.force_authenticate(self.other)

        response = self.client.put(
            f"/recipes/{recipe['id']}/image/",
            {"image": image_file()},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
