from django.core import mail
from rest_framework import status

from recipes.models import Recipe, RecipeSubmission

from .test_recipes import RecipeTestCase, image_file, recipe_payload


class ModerationTests(RecipeTestCase):
    def setUp(self):
        super().setUp()
        self.staff = self.create_user("staff@example.com", username="mod", is_staff=True)
        self.author.email_verified = True
        self.author.save()

    def moderate(self, submission_id, verb, **data):
        self.login(self.staff)

        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(
                f"/moderation/submissions/{submission_id}/{verb}", data
            )

    def test_new_recipe_notifies_staff(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.create_recipe()

        self.assertEqual(mail.outbox[0].to, ["staff@example.com"])

    def test_only_staff_may_moderate(self):
        self.create_recipe()

        response = self.client.get("/moderation/submissions")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_approve_new_recipe(self):
        data = self.create_recipe()
        submission = RecipeSubmission.objects.get()
        self.login(self.staff)

        listing = self.client.get("/moderation/submissions").json()
        response = self.moderate(submission.pk, "approve")
        again = self.moderate(submission.pk, "approve")

        self.assertEqual(listing["results"][0]["kind"], "new")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.json()["reviewed_by"], "mod")
        self.assertIsNone(response.json()["current"])
        self.assertEqual(Recipe.objects.get(pk=data["id"]).status, "approved")
        self.assertEqual(again.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(again.json()["code"], "submission_not_pending")
        self.assertIn("freigegeben", mail.outbox[-1].subject)

    def test_reject_needs_a_reason(self):
        self.create_recipe()
        submission = RecipeSubmission.objects.get()

        missing = self.moderate(submission.pk, "reject")
        response = self.moderate(submission.pk, "reject", reason="Zu wenig Schritte.")

        self.assertIn("reason", missing.json()["errors"])
        self.assertEqual(response.json()["status"], "rejected")
        recipe = Recipe.objects.get()
        self.assertEqual(recipe.status, "rejected")
        self.assertEqual(recipe.rejection_reason, "Zu wenig Schritte.")

    def test_approving_a_revision_replaces_the_live_version(self):
        data = self.create_recipe(approve=True)
        self.client.put(
            f"/recipes/{data['id']}",
            recipe_payload(name="Bessere Linsensuppe", prep_time_minutes=45),
        )
        self.client.put(
            f"/recipes/{data['id']}/image",
            {"image": image_file()},
            format="multipart",
        )
        revision = RecipeSubmission.objects.get(kind="revision")

        self.login(self.staff)
        detail = self.client.get(f"/moderation/submissions/{revision.pk}").json()
        self.moderate(revision.pk, "approve")
        self.login(self.author)
        recipe = self.client.get(f"/recipes/{data['id']}").json()

        self.assertEqual(detail["current"]["name"], "Rote Linsensuppe")
        self.assertEqual(detail["content"]["name"], "Bessere Linsensuppe")
        self.assertEqual(recipe["name"], "Bessere Linsensuppe")
        self.assertNotIn("under_30_min", recipe["properties"])
        self.assertIsNotNone(recipe["image_url"])
        self.assertIsNone(recipe["pending_revision"])

    def test_rejected_revision_keeps_the_live_version(self):
        data = self.create_recipe(approve=True)
        self.client.put(f"/recipes/{data['id']}", recipe_payload(name="Anders"))
        revision = RecipeSubmission.objects.get(kind="revision")

        self.moderate(revision.pk, "reject", reason="Bitte nicht.")
        self.login(self.author)
        recipe = self.client.get(f"/recipes/{data['id']}").json()

        self.assertEqual(recipe["name"], "Rote Linsensuppe")
        self.assertEqual(recipe["status"], "approved")
        self.assertEqual(recipe["pending_revision"]["status"], "rejected")
        self.assertEqual(recipe["pending_revision"]["rejection_reason"], "Bitte nicht.")

    def test_moderation_still_shows_the_username(self):
        self.create_recipe()
        self.login(self.staff)

        listing = self.client.get("/moderation/submissions").json()
        submission = listing["results"][0] if "results" in listing else listing[0]

        self.assertEqual(submission["author"], {"username": "koch"})
