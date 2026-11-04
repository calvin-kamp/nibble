from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.accounts.models import BodyProfile, ConsentRecord
from apps.foods.models import FoodProduct
from apps.tracking.models import GoalSetting, Meal, WeightEntry
from config.testing import ApiTestCase

ACCEPT = {"accepted": True, "policy_version": "2026-10-27"}
REVOKE = {"accepted": False, "policy_version": "2026-10-27"}


class OnboardingTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.create_user()
        self.login(self.user)

    def step(self):
        return self.client.get(reverse("onboarding")).data["current_step"]

    def test_full_onboarding_with_consent(self):
        self.client.patch(reverse("profile"), {"username": "gurke_42"})
        self.assertEqual(self.step(), "consent")

        self.client.put(
            reverse("privacy_consent"),
            {"accepted": True, "policy_version": "2026-10-27"},
        )
        self.assertEqual(self.step(), "goal")

        self.client.patch(reverse("goal"), {"goal": "lose"})
        self.assertEqual(self.step(), "targets")

        self.client.patch(
            reverse("goal"),
            {"targets": {"kcal": 2000, "protein": 120, "carbs": 220, "fat": 70}},
        )
        self.assertEqual(self.step(), "summary")

        response = self.client.post(reverse("onboarding_complete"))

        self.assertEqual(response.data, {"completed": True, "current_step": "summary"})

    def test_declining_consent_skips_goal_and_targets(self):
        self.client.patch(reverse("profile"), {"username": "gurke"})
        self.client.put(reverse("privacy_consent"), REVOKE)

        self.assertEqual(self.step(), "summary")
        self.assertEqual(
            self.client.patch(reverse("onboarding"), {"current_step": "goal"}).data[
                "code"
            ],
            "onboarding_step_not_allowed",
        )

    def test_steps_need_their_preconditions(self):
        response = self.client.patch(reverse("onboarding"), {"current_step": "consent"})
        complete = self.client.post(reverse("onboarding_complete"))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "onboarding_step_not_allowed")
        self.assertEqual(complete.status_code, status.HTTP_400_BAD_REQUEST)

    def test_username_may_be_shared(self):
        self.create_user("other@example.com", username="Gurke")

        shared = self.client.patch(reverse("profile"), {"username": "gurke"})
        invalid = self.client.patch(reverse("profile"), {"username": "a b"})

        self.assertEqual(shared.status_code, status.HTTP_200_OK)
        self.assertEqual(shared.data["username"], "gurke")
        self.assertIn("username", invalid.data["errors"])


class ConsentTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.create_user(username="gurke", consent=True)
        self.login(self.user)

    def test_tracking_needs_consent(self):
        self.client.put(reverse("privacy_consent"), REVOKE)

        response = self.client.get(reverse("goal"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["code"], "consent_required")

    def test_every_decision_needs_the_policy_version(self):
        accept = self.client.put(reverse("privacy_consent"), {"accepted": True})
        revoke = self.client.put(reverse("privacy_consent"), {"accepted": False})

        self.assertIn("policy_version", accept.data["errors"])
        self.assertIn("policy_version", revoke.data["errors"])
        self.assertFalse(ConsentRecord.objects.exists())

    def test_history_records_consent_and_revocation_with_version(self):
        self.client.put(
            reverse("privacy_consent"), {"accepted": True, "policy_version": "v1"}
        )
        self.client.put(
            reverse("privacy_consent"), {"accepted": False, "policy_version": "v1"}
        )
        response = self.client.put(
            reverse("privacy_consent"), {"accepted": True, "policy_version": "v2"}
        )

        history = list(ConsentRecord.objects.values_list("accepted", "policy_version"))
        self.assertEqual(history, [(True, "v1"), (False, "v1"), (True, "v2")])
        self.assertEqual(response.data["policy_version"], "v2")
        self.user.profile.refresh_from_db()
        self.assertEqual(
            ConsentRecord.objects.last().decided_at,
            self.user.profile.consent_decided_at,
        )

    def test_revocation_keeps_its_version_on_the_profile(self):
        self.client.put(reverse("privacy_consent"), REVOKE)

        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.consent_policy_version, "2026-10-27")
        self.assertEqual(ConsentRecord.objects.get().accepted, False)

    def test_history_is_deleted_with_the_account(self):
        self.client.put(reverse("privacy_consent"), ACCEPT)

        self.user.delete()

        self.assertFalse(ConsentRecord.objects.exists())

    def test_revoking_deletes_tracking_data(self):
        self.client.post(
            reverse("weights"), {"weight_kg": 80.5, "measured_on": "2026-01-05"}
        )
        self.client.patch(reverse("goal"), {"goal": "gain"})

        response = self.client.put(reverse("privacy_consent"), REVOKE)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["accepted"])
        self.assertFalse(WeightEntry.objects.exists())
        self.assertFalse(GoalSetting.objects.exists())

    def test_revoking_deletes_body_data_and_meals(self):
        FoodProduct.objects.create(
            code="4000000000001",
            name="Haferflocken",
            kcal_per_100=372,
            protein_per_100=13.5,
            carbs_per_100=58.7,
            fat_per_100=7,
            imported_at=timezone.now(),
        )
        self.client.patch(reverse("body"), {"height_cm": 180, "sex": "female"})
        self.client.post(
            reverse("meal-list"),
            {
                "name": "Porridge",
                "items": [{"off_code": "4000000000001", "amount": 60, "unit": "g"}],
            },
        )
        self.assertTrue(BodyProfile.objects.exists())
        self.assertTrue(Meal.objects.exists())

        self.client.put(reverse("privacy_consent"), REVOKE)

        self.assertFalse(BodyProfile.objects.exists())
        self.assertFalse(Meal.objects.exists())
        self.assertEqual(ConsentRecord.objects.count(), 1)
