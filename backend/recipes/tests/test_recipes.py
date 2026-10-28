from io import BytesIO, StringIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from PIL import Image, ImageCms
from rest_framework import status

from config.testing import ApiTestCase
from recipes.models import Recipe, RecipeSubmission
from recipes.utils import has_metadata


def recipe_payload(**overrides):
    """Valid RecipeInput body as the frontend sends it."""
    payload = {
        "name": "Rote Linsensuppe",
        "description": "Cremig und schnell.",
        "prep_time_minutes": 25,
        "diet": "vegan",
        "intolerances": ["gluten_free"],
        "equipment": ["stove", "mixer"],
        "meal_types": ["lunch", "dinner"],
        "servings": 4,
        "nutrition_per_serving": {"kcal": 380, "protein": 40.04, "carbs": 30, "fat": 8},
        "ingredients": [
            {"name": "Rote Linsen", "amount": 250, "unit": "g"},
            {"name": "Zwiebel", "amount": 1, "unit": "piece"},
        ],
        "steps": [
            {"step_number": 1, "text": "Zwiebel würfeln."},
            {"step_number": 2, "text": "Alles kochen und pürieren."},
        ],
    }
    payload.update(overrides)

    return payload


def image_file(name="bild.png", image_format="PNG"):
    buffer = BytesIO()
    Image.new("RGB", (8, 8), "orange").save(buffer, image_format)

    return SimpleUploadedFile(
        name, buffer.getvalue(), content_type=f"image/{image_format.lower()}"
    )


def photo_with_metadata():
    """A JPEG as phones write it: GPS position, orientation, XMP, IPTC, colour profile."""
    image = Image.new("RGB", (40, 20), "orange")
    exif = Image.Exif()
    exif[0x0110] = "Testphone"  # Model
    exif[0x0112] = 6  # Orientation: rotate 90° clockwise to display
    exif.get_ifd(0x8825).update(  # GPS position
        {1: "N", 2: (51.0, 21.0, 36.0), 3: "E", 4: (7.0, 28.0, 12.0)}
    )
    xmp = b'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF/></x:xmpmeta>'
    icc = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()

    buffer = BytesIO()
    image.save(buffer, "JPEG", exif=exif, xmp=xmp, icc_profile=icc)
    data = buffer.getvalue()

    # IPTC lives in an APP13 "Photoshop 3.0" segment, inserted right after SOI
    iptc = b"Photoshop 3.0\x00" + b"8BIM\x04\x04\x00\x00\x00\x00\x00\x07\x1c\x02\x78\x00\x02Hi\x00"
    segment = b"\xff\xed" + (len(iptc) + 2).to_bytes(2, "big") + iptc
    data = data[:2] + segment + data[2:]

    with Image.open(BytesIO(data)) as check:
        assert has_metadata(check) and "photoshop" in check.info, "fixture lost metadata"

    return SimpleUploadedFile("foto.jpg", data, content_type="image/jpeg")


def mpo_photo():
    """Two pictures in one file, as phones write them, the first one orange.

    Pillow writes no valid MPO with extra EXIF, so metadata removal itself is covered by
    the JPEG tests; here it is the MP index that has to go.
    """
    first = Image.new("RGB", (40, 20), "orange")
    second = Image.new("RGB", (40, 20), "blue")

    buffer = BytesIO()
    first.save(buffer, "MPO", save_all=True, append_images=[second])

    with Image.open(BytesIO(buffer.getvalue())) as check:
        assert check.format == "MPO" and check.n_frames == 2, "fixture is no MPO"

    return SimpleUploadedFile("foto.jpg", buffer.getvalue(), content_type="image/jpeg")


class RecipeTestCase(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.author = self.create_user("author@example.com", username="koch")
        self.other = self.create_user("other@example.com", username="gast")

    def create_recipe(self, approve=False, **overrides):
        self.login(self.author)
        response = self.client.post("/recipes", recipe_payload(**overrides))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        if approve:
            Recipe.objects.filter(pk=response.json()["id"]).update(
                status=Recipe.Status.APPROVED
            )
            RecipeSubmission.objects.update(status=Recipe.Status.APPROVED)

        return response.json()


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
        self.assertEqual(
            RecipeSubmission.objects.get().kind, RecipeSubmission.Kind.NEW
        )

    def test_pending_recipes_are_hidden_from_others(self):
        data = self.create_recipe()
        self.login(self.other)

        detail = self.client.get(f"/recipes/{data['id']}")
        listing = self.client.get("/recipes")

        self.assertEqual(detail.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(listing.json()["count"], 0)

    def test_mine_shows_own_recipes_in_any_status(self):
        self.create_recipe()

        listing = self.client.get("/recipes", {"mine": "true"})
        self.client.force_authenticate(None)
        anonymous = self.client.get("/recipes", {"mine": "true"})

        self.assertEqual(listing.json()["count"], 1)
        self.assertEqual(listing.json()["results"][0]["status"], "pending")
        self.assertEqual(anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_validation_errors_use_dot_notation(self):
        self.login(self.author)

        response = self.client.post(
            "/recipes",
            recipe_payload(
                ingredients=[{"name": "Salz", "amount": 0, "unit": "spoon"}],
                steps=[{"step_number": 2, "text": "Kochen."}],
                meal_types=[],
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.json()["errors"]
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
            response = self.client.get("/recipes", params)
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

            return sorted(item["name"] for item in response.json()["results"])

        self.assertEqual(names(diet="vegan"), ["Ofen-Gemüse", "Overnight Oats"])
        self.assertEqual(len(names(diet="pescetarian")), 3)
        self.assertEqual(
            names(equipment=["stove", "mixer"]), ["Fischcurry", "Overnight Oats"]
        )
        self.assertEqual(names(equipment=["stove"]), ["Overnight Oats"])
        self.assertEqual(names(meal_types=["breakfast", "snack"]), ["Overnight Oats"])
        self.assertEqual(names(q="CURRY"), ["Fischcurry"])
        self.assertEqual(
            self.client.get("/recipes", {"diet": "keto"}).json()["code"],
            "validation_error",
        )

    def test_only_the_author_may_edit(self):
        data = self.create_recipe(approve=True)
        self.login(self.other)

        update = self.client.put(f"/recipes/{data['id']}", recipe_payload())
        delete = self.client.delete(f"/recipes/{data['id']}")
        self.client.force_authenticate(None)
        anonymous = self.client.delete(f"/recipes/{data['id']}")

        self.assertEqual(update.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(update.json()["code"], "forbidden")
        self.assertEqual(delete.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_editing_a_rejected_recipe_resubmits_it(self):
        data = self.create_recipe()
        Recipe.objects.filter(pk=data["id"]).update(
            status=Recipe.Status.REJECTED, rejection_reason="Zu kurz."
        )
        RecipeSubmission.objects.update(status=Recipe.Status.REJECTED)

        response = self.client.put(
            f"/recipes/{data['id']}", recipe_payload(name="Linsensuppe")
        )

        self.assertEqual(response.json()["status"], "pending")
        self.assertIsNone(response.json()["rejection_reason"])
        self.assertEqual(response.json()["name"], "Linsensuppe")
        self.assertEqual(RecipeSubmission.objects.filter(status="pending").count(), 1)

    def test_editing_an_approved_recipe_creates_one_revision(self):
        data = self.create_recipe(approve=True)

        self.client.put(f"/recipes/{data['id']}", recipe_payload(name="Neu 1"))
        response = self.client.put(
            f"/recipes/{data['id']}", recipe_payload(name="Neu 2")
        )
        self.login(self.other)
        public = self.client.get(f"/recipes/{data['id']}").json()

        body = response.json()
        self.assertEqual(body["name"], "Rote Linsensuppe")
        self.assertEqual(body["pending_revision"]["content"]["name"], "Neu 2")
        self.assertEqual(
            RecipeSubmission.objects.filter(kind="revision", status="pending").count(), 1
        )
        self.assertEqual(public["name"], "Rote Linsensuppe")
        self.assertIsNone(public["pending_revision"])

    def test_image_upload_on_pending_and_approved_recipe(self):
        pending = self.create_recipe()
        approved = self.create_recipe(approve=True, name="Freigegeben")

        direct = self.client.put(
            f"/recipes/{pending['id']}/image",
            {"image": image_file()},
            format="multipart",
        )
        revision = self.client.put(
            f"/recipes/{approved['id']}/image",
            {"image": image_file("x.webp", "WEBP")},
            format="multipart",
        )
        wrong = self.client.put(
            f"/recipes/{pending['id']}/image",
            {"image": image_file("x.gif", "GIF")},
            format="multipart",
        )

        self.assertEqual(direct.status_code, status.HTTP_200_OK, direct.data)
        self.assertRegex(direct.json()["image_url"], r"/recipes/\d+-rote-linsensuppe")
        self.assertIsNone(revision.json()["image_url"])
        self.assertTrue(revision.json()["pending_revision"]["image_url"].endswith(".webp"))
        self.assertIn("image", wrong.json()["errors"])

    def test_public_responses_never_contain_the_username(self):
        data = self.create_recipe(approve=True)
        responses = {}

        for name, user in (("guest", None), ("other", self.other), ("author", self.author)):
            self.client.force_authenticate(user)
            responses[name] = (
                self.client.get("/recipes"),
                self.client.get(f"/recipes/{data['id']}"),
            )

        for listing, detail in responses.values():
            self.assertEqual(listing.status_code, status.HTTP_200_OK)
            self.assertEqual(detail.status_code, status.HTTP_200_OK)
            self.assertNotIn('"koch"', listing.content.decode())
            self.assertNotIn('"koch"', detail.content.decode())
            self.assertNotIn("author", listing.json()["results"][0])
            self.assertNotIn("author", detail.json())

        self.assertIsNone(responses["guest"][1].json()["is_own"])
        self.assertFalse(responses["other"][1].json()["is_own"])
        self.assertFalse(responses["other"][0].json()["results"][0]["is_own"])
        self.assertTrue(responses["author"][1].json()["is_own"])
        self.assertTrue(responses["author"][0].json()["results"][0]["is_own"])

    def test_uploaded_images_lose_their_metadata(self):
        recipe = self.create_recipe()

        response = self.client.put(
            f"/recipes/{recipe['id']}/image",
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
            f"/recipes/{recipe['id']}/image",
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
            f"/recipes/{recipe['id']}/image",
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
            f"/recipes/{other['id']}/image",
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

        saved = self.client.put(f"/recipes/{data['id']}/saved")
        listing = self.client.get("/recipes", {"saved": "true"}).json()
        removed = self.client.delete(f"/recipes/{data['id']}/saved")

        self.assertEqual(saved.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(listing["count"], 1)
        self.assertTrue(listing["results"][0]["is_saved"])
        self.assertEqual(removed.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.client.get(f"/recipes/{data['id']}").json()["is_saved"])

    def test_pending_recipes_cannot_be_saved(self):
        data = self.create_recipe()

        response = self.client.put(f"/recipes/{data['id']}/saved")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
