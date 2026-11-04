from io import StringIO

from django.core.management import call_command
from django.urls import reverse
from PIL import Image
from rest_framework import status

from apps.recipes.models import Recipe, RecipeSubmission
from apps.recipes.utils import has_metadata

from .test_utils import (
    RecipeTestCase,
    image_file,
    mpo_photo,
    photo_with_metadata,
    recipe_payload,
)


class RecipeApiTests(RecipeTestCase):
    def test_create_is_pending_with_computed_properties(self):
        data = self.create_recipe()

        self.assertEqual(data["status"], "pending")
        self.assertNotIn("author", data)
        self.assertTrue(data["is_own"])
        self.assertEqual(data["nutrition_per_serving"]["protein"], 40.0)
        self.assertEqual(
            data["properties"],
            ["protein_rich", "low_calorie", "few_ingredients", "under_30_min"],
        )
        self.assertFalse(data["is_saved"])
        self.assertEqual(RecipeSubmission.objects.get().kind, RecipeSubmission.Kind.NEW)

    def test_pending_recipes_are_hidden_from_others(self):
        data = self.create_recipe()
        self.login(self.other)

        detail = self.client.get(reverse("recipe-detail", kwargs={"pk": data["id"]}))
        listing = self.client.get(reverse("recipe-list"))

        self.assertEqual(detail.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(listing.data["count"], 0)

    def test_mine_shows_own_recipes_in_any_status(self):
        self.create_recipe()

        listing = self.client.get(reverse("recipe-list"), {"mine": "true"})
        self.client.force_authenticate(None)
        anonymous = self.client.get(reverse("recipe-list"), {"mine": "true"})

        self.assertEqual(listing.data["count"], 1)
        self.assertEqual(listing.data["results"][0]["status"], "pending")
        self.assertEqual(anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_validation_errors_use_dot_notation(self):
        self.login(self.author)

        response = self.client.post(
            reverse("recipe-list"),
            recipe_payload(
                ingredients=[{"name": "Salz", "amount": 0, "unit": "spoon"}],
                steps=[{"step_number": 2, "text": "Kochen."}],
                meal_types=[],
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data["errors"]
        self.assertIn("ingredients.0.amount", errors)
        self.assertIn("ingredients.0.unit", errors)
        self.assertIn("steps", errors)
        self.assertIn("meal_types", errors)

    def test_filters(self):
        self.create_recipe(approve=True, name="Ofen-Gemüse", equipment=["oven"])
        self.create_recipe(approve=True, name="Fischcurry", diet="pescetarian")
        self.create_recipe(
            approve=True, name="Overnight Oats", equipment=[], meal_types=["breakfast"]
        )
        self.client.force_authenticate(None)

        def names(**params):
            response = self.client.get(reverse("recipe-list"), params)
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

            return sorted(item["name"] for item in response.data["results"])

        self.assertEqual(names(diet="vegan"), ["Ofen-Gemüse", "Overnight Oats"])
        self.assertEqual(len(names(diet="pescetarian")), 3)
        self.assertEqual(
            names(equipment=["stove", "mixer"]), ["Fischcurry", "Overnight Oats"]
        )
        self.assertEqual(names(equipment=["stove"]), ["Overnight Oats"])
        self.assertEqual(names(meal_types=["breakfast", "snack"]), ["Overnight Oats"])
        self.assertEqual(names(q="CURRY"), ["Fischcurry"])
        self.assertEqual(
            self.client.get(reverse("recipe-list"), {"diet": "keto"}).data["code"],
            "validation_error",
        )

    def test_sort_by_popularity(self):
        quiet = self.create_recipe(approve=True, name="Linsensuppe")
        popular = self.create_recipe(approve=True, name="Ofen-Gemüse")
        newest = self.create_recipe(approve=True, name="Overnight Oats")

        for user in (self.author, self.other):
            self.login(user)
            self.client.put(reverse("recipe-saved", kwargs={"pk": popular["id"]}))

        self.login(self.other)
        self.client.put(reverse("recipe-saved", kwargs={"pk": quiet["id"]}))
        self.client.force_authenticate(None)

        def names(**params):
            response = self.client.get(reverse("recipe-list"), params)
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

            return [item["name"] for item in response.data["results"]]

        self.assertEqual(names(), ["Overnight Oats", "Ofen-Gemüse", "Linsensuppe"])
        self.assertEqual(names(sort="newest"), names())
        self.assertEqual(
            names(sort="popular"), ["Ofen-Gemüse", "Linsensuppe", "Overnight Oats"]
        )
        self.assertEqual(newest["name"], "Overnight Oats")
        self.assertEqual(
            self.client.get(reverse("recipe-list"), {"sort": "random"}).data["code"],
            "validation_error",
        )

        # Among the user's saved recipes the order still counts every user's bookmarks
        self.login(self.other)
        saved = self.client.get(
            reverse("recipe-list"), {"saved": "true", "sort": "popular"}
        ).data
        self.assertEqual(
            [item["name"] for item in saved["results"]],
            ["Ofen-Gemüse", "Linsensuppe"],
        )

    def test_only_the_author_may_edit(self):
        data = self.create_recipe(approve=True)
        self.login(self.other)

        update = self.client.put(
            reverse("recipe-detail", kwargs={"pk": data["id"]}), recipe_payload()
        )
        delete = self.client.delete(reverse("recipe-detail", kwargs={"pk": data["id"]}))
        self.client.force_authenticate(None)
        anonymous = self.client.delete(
            reverse("recipe-detail", kwargs={"pk": data["id"]})
        )

        self.assertEqual(update.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(update.data["code"], "forbidden")
        self.assertEqual(delete.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_editing_a_rejected_recipe_resubmits_it(self):
        data = self.create_recipe()
        Recipe.objects.filter(pk=data["id"]).update(
            status=Recipe.Status.REJECTED, rejection_reason="Zu kurz."
        )
        RecipeSubmission.objects.update(status=Recipe.Status.REJECTED)

        response = self.client.put(
            reverse("recipe-detail", kwargs={"pk": data["id"]}),
            recipe_payload(name="Linsensuppe"),
        )

        self.assertEqual(response.data["status"], "pending")
        self.assertIsNone(response.data["rejection_reason"])
        self.assertEqual(response.data["name"], "Linsensuppe")
        self.assertEqual(RecipeSubmission.objects.filter(status="pending").count(), 1)

    def test_editing_an_approved_recipe_creates_one_revision(self):
        data = self.create_recipe(approve=True)

        self.client.put(
            reverse("recipe-detail", kwargs={"pk": data["id"]}),
            recipe_payload(name="Neu 1"),
        )
        response = self.client.put(
            reverse("recipe-detail", kwargs={"pk": data["id"]}),
            recipe_payload(name="Neu 2"),
        )
        self.login(self.other)
        public = self.client.get(
            reverse("recipe-detail", kwargs={"pk": data["id"]})
        ).data

        body = response.data
        self.assertEqual(body["name"], "Rote Linsensuppe")
        self.assertEqual(body["pending_revision"]["content"]["name"], "Neu 2")
        self.assertEqual(
            RecipeSubmission.objects.filter(kind="revision", status="pending").count(),
            1,
        )
        self.assertEqual(public["name"], "Rote Linsensuppe")
        self.assertIsNone(public["pending_revision"])

    def test_image_upload_on_pending_and_approved_recipe(self):
        pending = self.create_recipe()
        approved = self.create_recipe(approve=True, name="Freigegeben")

        direct = self.client.put(
            reverse("recipe-image", kwargs={"pk": pending["id"]}),
            {"image": image_file()},
            format="multipart",
        )
        revision = self.client.put(
            reverse("recipe-image", kwargs={"pk": approved["id"]}),
            {"image": image_file("x.webp", "WEBP")},
            format="multipart",
        )
        wrong = self.client.put(
            reverse("recipe-image", kwargs={"pk": pending["id"]}),
            {"image": image_file("x.gif", "GIF")},
            format="multipart",
        )

        self.assertEqual(direct.status_code, status.HTTP_200_OK, direct.data)
        self.assertRegex(direct.data["image_url"], r"/recipes/\d+-rote-linsensuppe")
        self.assertIsNone(revision.data["image_url"])
        self.assertTrue(
            revision.data["pending_revision"]["image_url"].endswith(".webp")
        )
        self.assertIn("image", wrong.data["errors"])

    def test_public_responses_never_contain_the_username(self):
        data = self.create_recipe(approve=True)
        responses = {}

        for name, user in (
            ("guest", None),
            ("other", self.other),
            ("author", self.author),
        ):
            self.client.force_authenticate(user)
            responses[name] = (
                self.client.get(reverse("recipe-list")),
                self.client.get(reverse("recipe-detail", kwargs={"pk": data["id"]})),
            )

        for listing, detail in responses.values():
            self.assertEqual(listing.status_code, status.HTTP_200_OK)
            self.assertEqual(detail.status_code, status.HTTP_200_OK)
            self.assertNotIn('"koch"', listing.content.decode())
            self.assertNotIn('"koch"', detail.content.decode())
            self.assertNotIn("author", listing.data["results"][0])
            self.assertNotIn("author", detail.data)

        self.assertIsNone(responses["guest"][1].data["is_own"])
        self.assertFalse(responses["other"][1].data["is_own"])
        self.assertFalse(responses["other"][0].data["results"][0]["is_own"])
        self.assertTrue(responses["author"][1].data["is_own"])
        self.assertTrue(responses["author"][0].data["results"][0]["is_own"])

    def test_uploaded_images_lose_their_metadata(self):
        recipe = self.create_recipe()

        response = self.client.put(
            reverse("recipe-image", kwargs={"pk": recipe["id"]}),
            {"image": photo_with_metadata()},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        stored = Recipe.objects.get(pk=recipe["id"]).image

        with stored.open("rb") as file, Image.open(file) as image:
            self.assertEqual(image.format, "JPEG")
            self.assertFalse(has_metadata(image))
            self.assertEqual(len(image.getexif()), 0)
            self.assertNotIn("xmp", image.info)
            self.assertNotIn("photoshop", image.info)
            # Orientation 6 (turned right) is applied to the pixels: 40x20 becomes 20x40
            self.assertEqual(image.size, (20, 40))
            self.assertIn("icc_profile", image.info)

    def test_mpo_photos_are_stored_as_jpeg(self):
        recipe = self.create_recipe()

        response = self.client.put(
            reverse("recipe-image", kwargs={"pk": recipe["id"]}),
            {"image": mpo_photo()},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        stored = Recipe.objects.get(pk=recipe["id"]).image
        self.assertTrue(stored.name.endswith(".jpg"))

        with stored.open("rb") as file, Image.open(file) as image:
            self.assertEqual(image.format, "JPEG")
            self.assertEqual(getattr(image, "n_frames", 1), 1)
            self.assertFalse(has_metadata(image))
            # The first picture, not the second one
            red, green, blue = image.convert("RGB").getpixel((20, 10))
            self.assertGreater(red, 200)
            self.assertLess(blue, 80)

    def test_revision_images_lose_their_metadata(self):
        recipe = self.create_recipe(approve=True)

        self.client.put(
            reverse("recipe-image", kwargs={"pk": recipe["id"]}),
            {"image": photo_with_metadata()},
            format="multipart",
        )

        stored = RecipeSubmission.objects.get(kind=RecipeSubmission.Kind.REVISION).image

        with stored.open("rb") as file, Image.open(file) as image:
            self.assertFalse(has_metadata(image))
            self.assertEqual(image.size, (20, 40))

    def test_command_cleans_stored_images(self):
        recipe = self.create_recipe()
        stored = Recipe.objects.get(pk=recipe["id"])
        stored.image.save("image.jpg", photo_with_metadata())
        other = self.create_recipe(name="Sauber")
        self.client.put(
            reverse("recipe-image", kwargs={"pk": other["id"]}),
            {"image": image_file()},
            format="multipart",
        )
        clean_before = Recipe.objects.get(pk=other["id"]).image.read()

        dry_run = StringIO()
        call_command("strip_image_metadata", "--dry-run", stdout=dry_run)

        with stored.image.open("rb") as file, Image.open(file) as image:
            self.assertTrue(has_metadata(image))

        output = StringIO()
        call_command("strip_image_metadata", stdout=output)

        self.assertIn("1 of 2 images carry metadata", dry_run.getvalue())
        self.assertIn("1 of 2 images cleaned", output.getvalue())

        with stored.image.open("rb") as file, Image.open(file) as image:
            self.assertFalse(has_metadata(image))
            self.assertEqual(image.size, (20, 40))

        self.assertEqual(Recipe.objects.get(pk=other["id"]).image.read(), clean_before)

    def test_save_and_unsave(self):
        data = self.create_recipe(approve=True)
        self.login(self.other)

        saved = self.client.put(reverse("recipe-saved", kwargs={"pk": data["id"]}))
        listing = self.client.get(reverse("recipe-list"), {"saved": "true"}).data
        removed = self.client.delete(reverse("recipe-saved", kwargs={"pk": data["id"]}))

        self.assertEqual(saved.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(listing["count"], 1)
        self.assertTrue(listing["results"][0]["is_saved"])
        self.assertEqual(removed.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            self.client.get(reverse("recipe-detail", kwargs={"pk": data["id"]})).data[
                "is_saved"
            ]
        )

    def test_pending_recipes_cannot_be_saved(self):
        data = self.create_recipe()

        response = self.client.put(reverse("recipe-saved", kwargs={"pk": data["id"]}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
