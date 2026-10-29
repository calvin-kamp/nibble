from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image, ImageCms
from rest_framework import status

from apps.recipes.models import Recipe, RecipeSubmission
from apps.recipes.utils import has_metadata
from config.testing import ApiTestCase


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
