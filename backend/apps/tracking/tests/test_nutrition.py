from datetime import timedelta

from rest_framework import status

from apps.foods.models import FoodProduct
from apps.tracking.models import GoalSetting

from .test_utils import MILK, OATS, TrackingTestCase


class EntryTests(TrackingTestCase):
    def test_values_are_computed_from_amount_and_unit(self):
        grams = self.track(amount=50).json()
        portions = self.track(amount=1.5, unit="portion").json()

        self.assertEqual(grams["kcal"], 186.0)
        self.assertEqual(grams["protein"], 6.8)
        self.assertEqual(grams["nutrition_per_100"]["carbs"], 58.7)
        self.assertEqual(grams["source"], "off")
        # 1.5 portions of 40 g = 60 g
        self.assertEqual(portions["kcal"], 223.2)
        self.assertEqual(portions["serving_quantity"], 40.0)

    def test_unit_must_fit_the_product(self):
        wrong_unit = self.track(code=MILK, unit="g")
        no_portion = self.track(code=MILK, unit="portion")
        unknown = self.track(code="12345678")

        self.assertIn("unit", wrong_unit.json()["errors"])
        self.assertIn("unit", no_portion.json()["errors"])
        self.assertIn("off_code", unknown.json()["errors"])

    def test_future_dates_are_rejected(self):
        response = self.track(consumed_on=self.today + timedelta(days=1))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["code"], "future_date_not_allowed")
        self.assertIn("consumed_on", response.json()["errors"])

    def test_patch_recalculates_from_stored_values(self):
        entry = self.track(amount=100).json()
        FoodProduct.objects.filter(code=OATS).update(kcal_per_100=999)

        response = self.client.patch(
            f"/tracking/entries/{entry['id']}", {"amount": 200}
        )

        self.assertEqual(response.json()["kcal"], 744.0)

    def test_entries_of_others_are_not_found(self):
        entry = self.track().json()
        self.login(self.create_user("other@example.com", consent=True))

        response = self.client.delete(f"/tracking/entries/{entry['id']}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class MealTests(TrackingTestCase):
    def create_meal(self):
        return self.client.post(
            "/tracking/meals",
            {
                "name": "Porridge",
                "items": [
                    {"off_code": OATS, "amount": 60, "unit": "g"},
                    {"off_code": MILK, "amount": 200, "unit": "ml"},
                ],
            },
        ).json()

    def test_meal_totals(self):
        meal = self.create_meal()

        # 60 g oats (223.2 kcal) + 200 ml milk (94 kcal)
        self.assertEqual(meal["totals"]["kcal"], 317.2)
        self.assertEqual(meal["items"][1]["food_name"], "Milch 1,5 %")

    def test_track_meal_and_only_change_date_and_meal_type(self):
        meal = self.create_meal()

        entry = self.client.post(
            "/tracking/entries/from-meal",
            {"meal_id": meal["id"], "consumed_on": str(self.today), "meal_type": "lunch"},
        ).json()
        amount = self.client.patch(
            f"/tracking/entries/{entry['id']}", {"amount": 2}
        )
        meal_type = self.client.patch(
            f"/tracking/entries/{entry['id']}", {"meal_type": "dinner"}
        )

        self.assertEqual(entry["source"], "meal")
        self.assertEqual(entry["unit"], "portion")
        self.assertIsNone(entry["nutrition_per_100"])
        self.assertEqual(entry["kcal"], meal["totals"]["kcal"])
        self.assertIn("amount", amount.json()["errors"])
        self.assertEqual(meal_type.json()["meal_type"], "dinner")

    def test_note_is_saved_changed_and_cleared(self):
        items = [{"off_code": OATS, "amount": 60, "unit": "g"}]
        meal = self.client.post(
            "/tracking/meals",
            {"name": "Porridge", "note": "  Mit Zimt  ", "items": items},
        ).json()
        changed = self.client.put(
            f"/tracking/meals/{meal['id']}",
            {"name": "Porridge", "note": "Ohne Zucker", "items": items},
        ).json()
        cleared = self.client.put(
            f"/tracking/meals/{meal['id']}", {"name": "Porridge", "items": items}
        ).json()

        self.assertEqual(meal["note"], "Mit Zimt")
        self.assertEqual(changed["note"], "Ohne Zucker")
        self.assertEqual(cleared["note"], "")
        self.assertEqual(self.create_meal()["note"], "")

    def test_note_is_limited_and_needs_consent(self):
        items = [{"off_code": OATS, "amount": 60, "unit": "g"}]
        too_long = self.client.post(
            "/tracking/meals", {"name": "Lang", "note": "x" * 301, "items": items}
        )
        self.user.profile.consent_accepted = False
        self.user.profile.save()
        without_consent = self.client.post(
            "/tracking/meals", {"name": "Neu", "note": "Notiz", "items": items}
        )

        self.assertIn("note", too_long.json()["errors"])
        self.assertEqual(without_consent.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(without_consent.json()["code"], "consent_required")

    def test_meal_item_errors_point_to_the_item(self):
        response = self.client.post(
            "/tracking/meals",
            {"name": "Kaputt", "items": [{"off_code": OATS, "amount": 1, "unit": "ml"}]},
        )

        self.assertIn("items.0.unit", response.json()["errors"])


class DaySummaryTests(TrackingTestCase):
    def test_summary_compares_with_targets_valid_on_that_day(self):
        yesterday = self.today - timedelta(days=1)
        GoalSetting.objects.create(
            profile=self.user.profile,
            valid_from=yesterday - timedelta(days=10),
            goal="lose",
            kcal=1800,
            protein=100,
            carbs=200,
            fat=60,
        )
        self.client.patch(
            "/tracking/goal",
            {"targets": {"kcal": 2500, "protein": 150, "carbs": 300, "fat": 80}},
        )
        self.track(amount=100, consumed_on=yesterday)
        self.track(amount=50, consumed_on=yesterday, meal_type="snack")

        summary = self.client.get(f"/tracking/days/{yesterday}").json()
        goal = self.client.get("/tracking/goal").json()

        self.assertEqual(summary["targets"]["kcal"], 1800.0)
        self.assertEqual(summary["intake"]["kcal"], 558.0)
        self.assertEqual(summary["difference"]["kcal"], 558.0 - 1800)
        self.assertEqual(set(summary["by_meal_type"]), {"breakfast", "snack"})
        self.assertEqual(len(summary["entries"]), 2)
        self.assertEqual(goal["goal"], "lose")
        self.assertEqual(goal["targets"]["kcal"], 2500.0)
        self.assertEqual(goal["valid_from"], str(self.today))

    def test_day_without_targets_and_entries(self):
        summary = self.client.get(f"/tracking/days/{self.today}").json()
        invalid = self.client.get("/tracking/days/gestern")

        self.assertIsNone(summary["targets"])
        self.assertIsNone(summary["difference"])
        self.assertEqual(summary["intake"]["kcal"], 0)
        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)

    def test_goal_without_input_is_empty(self):
        response = self.client.get("/tracking/goal")

        self.assertEqual(
            response.json(), {"goal": None, "targets": None, "valid_from": None}
        )

    def test_targets_have_limits(self):
        response = self.client.patch(
            "/tracking/goal",
            {"targets": {"kcal": 100, "protein": 1, "carbs": 1, "fat": 1}},
        )

        self.assertIn("targets.kcal", response.json()["errors"])
