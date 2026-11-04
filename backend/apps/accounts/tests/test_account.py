from datetime import timedelta

from django.conf import settings
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.accounts.models import Profile, User
from apps.accounts.tasks import delete_expired_accounts
from apps.foods.models import FoodProduct
from apps.recipes.models import Recipe, RecipeSubmission
from apps.recipes.tests.test_utils import recipe_payload
from config.testing import PASSWORD, ApiTestCase


class AccountDeletionTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.create_user(
            username="gurke", consent=True, email_verified=True
        )
        self.login(self.user)

    def test_deletion_needs_the_password(self):
        response = self.client.post(reverse("account_deletion"), {"password": "falsch"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data["errors"])

    def test_deletion_is_scheduled_and_can_be_cancelled(self):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("account_deletion"), {"password": PASSWORD}
            )

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertAlmostEqual(
            self.user.deletion_scheduled_for,
            timezone.now() + timedelta(days=7),
            delta=timedelta(minutes=1),
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIsNotNone(
            self.client.get(reverse("current_account")).data["deletion_scheduled_for"]
        )

        cancelled = self.client.delete(reverse("account_deletion"))
        again = self.client.delete(reverse("account_deletion"))

        self.assertEqual(cancelled.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(again.data["code"], "not_found")

    def test_daily_job_deletes_expired_accounts_but_keeps_approved_recipes(self):
        approved = self.client.post(reverse("recipe-list"), recipe_payload()).data
        self.client.post(reverse("recipe-list"), recipe_payload(name="Entwurf"))
        Recipe.objects.filter(pk=approved["id"]).update(status=Recipe.Status.APPROVED)

        self.user.deletion_scheduled_for = timezone.now() - timedelta(minutes=1)
        self.user.save()
        keeper = self.create_user("bleibt@example.com")
        keeper.deletion_scheduled_for = timezone.now() + timedelta(days=1)
        keeper.save()

        self.assertEqual(delete_expired_accounts(), 1)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
        self.assertFalse(Profile.objects.filter(username="gurke").exists())
        self.assertTrue(User.objects.filter(pk=keeper.pk).exists())
        self.assertEqual(
            list(Recipe.objects.values_list("pk", "author")), [(approved["id"], None)]
        )


class AccountExportTests(ApiTestCase):
    def test_export_contains_the_users_data(self):
        user = self.create_user(username="gurke", consent=True)
        self.login(user)
        self.client.post(
            reverse("weights"), {"weight_kg": 80.5, "measured_on": "2026-01-05"}
        )

        response = self.client.get(reverse("account_export"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("attachment", response.headers["Content-Disposition"])
        data = response.data
        self.assertEqual(data["account"]["email"], "user@example.com")
        self.assertEqual(data["profile"]["username"], "gurke")
        self.assertEqual(data["weights"][0]["weight_kg"], 80.5)
        self.assertEqual(data["recipes"], [])
        self.assertEqual(data["submissions"], [])
        self.assertNotIn("password", str(data))

    def test_export_contains_every_documented_part(self):
        user = self.create_user(username="gurke", consent=None)
        user.last_login = timezone.now()
        user.deletion_scheduled_for = timezone.now() + timedelta(days=7)
        user.save()
        user.profile.terms_accepted_at = timezone.now()
        user.profile.terms_version = "2026-11-01"
        user.profile.save()
        self.login(user)
        FoodProduct.objects.create(
            code="4000000000001",
            name="Haferflocken",
            kcal_per_100=372,
            protein_per_100=13.5,
            carbs_per_100=58.7,
            fat_per_100=7,
            imported_at=timezone.now(),
        )
        self.client.put(
            reverse("privacy_consent"),
            {"accepted": False, "policy_version": "2026-10-01"},
        )
        self.client.put(
            reverse("privacy_consent"),
            {"accepted": True, "policy_version": "2026-10-27"},
        )
        self.client.patch(reverse("body"), {"birth_date": "1990-05-17"})
        self.client.post(
            reverse("meal-list"),
            {
                "name": "Porridge",
                "items": [{"off_code": "4000000000001", "amount": 60, "unit": "g"}],
            },
        )
        recipe = self.client.post(reverse("recipe-list"), recipe_payload()).data
        RecipeSubmission.objects.filter(recipe_id=recipe["id"]).update(
            status=Recipe.Status.REJECTED, rejection_reason="Zu wenig Schritte."
        )

        data = self.client.get(reverse("account_export")).data

        self.assertIsNotNone(data["account"]["last_login"])
        self.assertIsNotNone(data["account"]["deletion_scheduled_for"])
        self.assertIsNotNone(data["account"]["terms_accepted_at"])
        self.assertEqual(data["account"]["terms_version"], "2026-11-01")
        self.assertEqual(
            data["account"]["privacy_policy_version"], settings.PRIVACY_POLICY_VERSION
        )
        self.assertEqual(
            data["onboarding"], {"completed": False, "current_step": "username"}
        )
        self.assertEqual(
            [(r["accepted"], r["policy_version"]) for r in data["consent_history"]],
            [(False, "2026-10-01"), (True, "2026-10-27")],
        )
        self.assertEqual(data["body"]["birth_date"], "1990-05-17")
        self.assertEqual(data["meals"][0]["name"], "Porridge")
        self.assertEqual(data["submissions"][0]["status"], "rejected")
        self.assertEqual(
            data["submissions"][0]["rejection_reason"], "Zu wenig Schritte."
        )
        self.assertEqual(data["submissions"][0]["recipe_id"], recipe["id"])
        self.assertNotIn("reviewed_by", data["submissions"][0])

    def test_export_without_consent_leaves_out_health_data(self):
        user = self.create_user(username="gurke", consent=False)
        self.login(user)

        data = self.client.get(reverse("account_export")).data

        for key in ("body", "goal_history", "weights", "entries", "meals"):
            self.assertNotIn(key, data)
        self.assertEqual(data["consent_history"], [])
