from django.utils import timezone
from rest_framework import status

from config.testing import ApiTestCase
from recipes.models import Recipe
from recipes.tests.test_recipes import recipe_payload


class PublicStatsTests(ApiTestCase):
    def test_counts_only_what_the_public_may_see(self):
        author = self.create_user("author@example.com", username="koch")
        self.create_user("staff@example.com", is_staff=True)
        self.create_user("leaving@example.com", deletion_scheduled_for=timezone.now())

        self.login(author)
        for name in ("Linsensuppe", "Porridge"):
            response = self.client.post("/recipes", recipe_payload(name=name))
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        Recipe.objects.filter(name="Porridge").update(status=Recipe.Status.APPROVED)

        self.client.force_authenticate(None)
        response = self.client.get("/stats")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"users": 1, "recipes": 1, "foods": 0, "entries": 0})

    def test_invalid_cookie_does_not_block_the_public_numbers(self):
        self.client.cookies["access_token"] = "kaputt"

        response = self.client.get("/stats")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
