from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.foods.models import FoodProduct
from apps.recipes.models import Recipe
from apps.recipes.tests.test_utils import recipe_payload
from config.testing import ApiTestCase


class PublicStatsTests(ApiTestCase):
    def test_counts_only_what_the_public_may_see(self):
        author = self.create_user("author@example.com", username="koch")
        self.create_user("staff@example.com", is_staff=True)
        self.create_user("leaving@example.com", deletion_scheduled_for=timezone.now())

        self.login(author)
        for name in ("Linsensuppe", "Porridge"):
            response = self.client.post(
                reverse("recipe-list"), recipe_payload(name=name)
            )
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, response.data
            )
        Recipe.objects.filter(name="Porridge").update(status=Recipe.Status.APPROVED)

        self.client.force_authenticate(None)
        response = self.client.get(reverse("public_stats"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            # The generic foods (banana etc.) come with a migration.
            {"users": 1, "recipes": 1, "foods": FoodProduct.objects.count(), "entries": 0},
        )

    def test_invalid_cookie_does_not_block_the_public_numbers(self):
        self.client.cookies["access_token"] = "kaputt"

        response = self.client.get(reverse("public_stats"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
