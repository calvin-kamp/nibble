from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.recipes.models import Recipe, RecipeSubmission

from .test_utils import RecipeTestCase, image_file


class RecipeMediaTests(RecipeTestCase):
    """Images are served by Django, so they follow the same visibility as the recipes."""

    def client_for(self, user=None):
        client = APIClient()

        if user is not None:
            client.cookies[settings.AUTH_COOKIE["ACCESS_NAME"]] = str(
                AccessToken.for_user(user)
            )

        return client

    @staticmethod
    def media_url(name):
        return reverse("recipe_media", kwargs={"path": name})

    def upload(self, recipe_id):
        self.login(self.author)
        response = self.client.put(
            reverse("recipe-image", kwargs={"pk": recipe_id}),
            {"image": image_file()},
            format="multipart",
        )
        self.assertIn(
            response.status_code, (status.HTTP_200_OK, status.HTTP_202_ACCEPTED)
        )

    def test_pending_image_only_for_author_and_staff(self):
        recipe = self.create_recipe()
        self.upload(recipe["id"])
        url = self.media_url(Recipe.objects.get(pk=recipe["id"]).image.name)
        staff = self.create_user("staff@example.com", is_staff=True)

        self.assertEqual(
            self.client_for().get(url).status_code, status.HTTP_404_NOT_FOUND
        )
        self.assertEqual(
            self.client_for(self.other).get(url).status_code, status.HTTP_404_NOT_FOUND
        )

        own = self.client_for(self.author).get(url)
        self.assertEqual(own.status_code, status.HTTP_200_OK)
        self.assertEqual(own["Cache-Control"], "private, no-store")
        self.assertEqual(
            self.client_for(staff).get(url).status_code, status.HTTP_200_OK
        )

    def test_approved_image_is_public(self):
        recipe = self.create_recipe()
        self.upload(recipe["id"])
        Recipe.objects.filter(pk=recipe["id"]).update(status=Recipe.Status.APPROVED)
        url = self.media_url(Recipe.objects.get(pk=recipe["id"]).image.name)

        response = self.client_for().get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("no-store", response.get("Cache-Control", ""))

    def test_pending_revision_image_is_not_public(self):
        recipe = self.create_recipe(approve=True)
        self.upload(recipe["id"])
        submission = RecipeSubmission.objects.exclude(image="").get()
        url = self.media_url(submission.image.name)

        self.assertEqual(
            self.client_for().get(url).status_code, status.HTTP_404_NOT_FOUND
        )
        self.assertEqual(
            self.client_for(self.author).get(url).status_code, status.HTTP_200_OK
        )

    def test_unknown_file_is_not_found(self):
        response = self.client_for().get(
            self.media_url("recipes/999-gibt-es-nicht.jpg")
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
