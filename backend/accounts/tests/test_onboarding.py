from django.utils import timezone
from rest_framework import status

from accounts.models import ConsentRecord
from config.testing import ApiTestCase
from foods.models import FoodProduct
from tracking.models import BodyProfile, GoalSetting, Meal, WeightEntry

ACCEPT = {"accepted": True, "policy_version": "2026-10-27"}
REVOKE = {"accepted": False, "policy_version": "2026-10-27"}


class OnboardingTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.create_user()
        self.login(self.user)

    def step(self):
        return self.client.get("/onboarding").json()["current_step"]

    def test_full_onboarding_with_consent(self):
        self.client.patch("/profile", {"username": "gurke_42"})
        self.assertEqual(self.step(), "consent")

        self.client.put(
            "/privacy/consent", {"accepted": True, "policy_version": "2026-10-27"}
        )
        self.assertEqual(self.step(), "goal")

        self.client.patch("/tracking/goal", {"goal": "lose"})
        self.assertEqual(self.step(), "targets")

        self.client.patch(
            "/tracking/goal",
            {"targets": {"kcal": 2000, "protein": 120, "carbs": 220, "fat": 70}},
        )
        self.assertEqual(self.step(), "summary")

        response = self.client.post("/onboarding/complete")

        self.assertEqual(response.json(), {"completed": True, "current_step": "summary"})

    def test_declining_consent_skips_goal_and_targets(self):
        self.client.patch("/profile", {"username": "gurke"})
        self.client.put("/privacy/consent", REVOKE)

        self.assertEqual(self.step(), "summary")
        self.assertEqual(
            self.client.patch("/onboarding", {"current_step": "goal"}).json()["code"],
            "onboarding_step_not_allowed",
        )

    def test_steps_need_their_preconditions(self):
        response = self.client.patch("/onboarding", {"current_step": "consent"})
        complete = self.client.post("/onboarding/complete")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["code"], "onboarding_step_not_allowed")
        self.assertEqual(complete.status_code, status.HTTP_400_BAD_REQUEST)

    def test_username_is_unique_ignoring_case(self):
        self.create_user("other@example.com", username="Gurke")

        taken = self.client.patch("/profile", {"username": "gurke"})
        invalid = self.client.patch("/profile", {"username": "a b"})
        available = self.client.get(
            "/profile/username-availability", {"username": "GURKE"}
        )

        self.assertEqual(taken.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(taken.json()["code"], "username_taken")
        self.assertIn("username", invalid.json()["errors"])
        self.assertEqual(available.json(), {"username": "GURKE", "available": False})

    def test_own_username_counts_as_available(self):
        self.client.patch("/profile", {"username": "Gurke"})

        response = self.client.get(
            "/profile/username-availability", {"username": "gurke"}
        )

        self.assertTrue(response.json()["available"])


class ConsentTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.create_user(username="gurke", consent=True)
        self.login(self.user)

    def test_tracking_needs_consent(self):
        self.client.put("/privacy/consent", REVOKE)

        response = self.client.get("/tracking/goal")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["code"], "consent_required")

    def test_every_decision_needs_the_policy_version(self):
        accept = self.client.put("/privacy/consent", {"accepted": True})
        revoke = self.client.put("/privacy/consent", {"accepted": False})

        self.assertIn("policy_version", accept.json()["errors"])
        self.assertIn("policy_version", revoke.json()["errors"])
        self.assertFalse(ConsentRecord.objects.exists())

    def test_history_records_consent_and_revocation_with_version(self):
        self.client.put("/privacy/consent", {"accepted": True, "policy_version": "v1"})
        self.client.put("/privacy/consent", {"accepted": False, "policy_version": "v1"})
        response = self.client.put(
            "/privacy/consent", {"accepted": True, "policy_version": "v2"}
        )

        history = list(
            ConsentRecord.objects.values_list("accepted", "policy_version")
        )
        self.assertEqual(history, [(True, "v1"), (False, "v1"), (True, "v2")])
        self.assertEqual(response.json()["policy_version"], "v2")
        self.user.profile.refresh_from_db()
        self.assertEqual(
            ConsentRecord.objects.last().decided_at, self.user.profile.consent_decided_at
        )

    def test_revocation_keeps_its_version_on_the_profile(self):
        self.client.put("/privacy/consent", REVOKE)

        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.consent_policy_version, "2026-10-27")
        self.assertEqual(ConsentRecord.objects.get().accepted, False)

    def test_history_is_deleted_with_the_account(self):
        self.client.put("/privacy/consent", ACCEPT)

        self.user.delete()

        self.assertFalse(ConsentRecord.objects.exists())

    def test_revoking_deletes_tracking_data(self):
        self.client.post(
            "/tracking/weights", {"weight_kg": 80.5, "measured_on": "2026-01-05"}
        )
        self.client.patch("/tracking/goal", {"goal": "gain"})

        response = self.client.put("/privacy/consent", REVOKE)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.json()["accepted"])
        self.assertFalse(WeightEntry.objects.exists())
        self.assertFalse(GoalSetting.objects.exists())

    def test_revoking_deletes_body_data_and_meals_with_notes(self):
        FoodProduct.objects.create(
            code="4000000000001",
            name="Haferflocken",
            kcal_per_100=372,
            protein_per_100=13.5,
            carbs_per_100=58.7,
            fat_per_100=7,
            imported_at=timezone.now(),
        )
        self.client.patch("/tracking/body", {"height_cm": 180, "sex": "female"})
        self.client.post(
            "/tracking/meals",
            {
                "name": "Porridge",
                "note": "Mit Zimt",
                "items": [{"off_code": "4000000000001", "amount": 60, "unit": "g"}],
            },
        )
        self.assertTrue(BodyProfile.objects.exists())
        self.assertTrue(Meal.objects.filter(note="Mit Zimt").exists())

        self.client.put("/privacy/consent", REVOKE)

        self.assertFalse(BodyProfile.objects.exists())
        self.assertFalse(Meal.objects.exists())
        self.assertEqual(ConsentRecord.objects.count(), 1)
