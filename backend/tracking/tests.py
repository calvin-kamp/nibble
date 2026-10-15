from datetime import date, timedelta
from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Profile
from food.models import Basis, Food, FoodUnit
from tracking.models import (
    BodyData,
    DailyGoal,
    DiaryEntry,
    Meal,
    MealItem,
    WeightEntry,
)
from tracking.weight import stats_of, weeks_of

TODAY = timezone.localdate()


def food(name, kcal, protein, carbs, fat, basis=Basis.GRAM, brand=""):
    return Food.objects.create(
        name=name,
        brand=brand,
        basis=basis,
        kcal_per_100=Decimal(str(kcal)),
        protein_per_100=Decimal(str(protein)),
        carbs_per_100=Decimal(str(carbs)),
        fat_per_100=Decimal(str(fat)),
    )


class TrackingTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model().objects
        cls.user = users.create_user(email="ich@example.com", password="x")
        cls.other = users.create_user(email="du@example.com", password="x")
        Profile.objects.create(user=cls.user, data_consent=True)
        Profile.objects.create(user=cls.other, data_consent=True)
        cls.stranger = users.create_user(email="neu@example.com", password="x")
        Profile.objects.create(user=cls.stranger)
        DailyGoal.objects.create(
            owner=cls.user,
            valid_from=TODAY - timedelta(days=30),
            source=DailyGoal.Source.CALCULATED,
            kcal=2180,
            protein=140,
            carbs=245,
            fat=70,
            weight=Decimal("78.4"),
        )

        cls.oats = food("Haferflocken, kernig", 368, 13.5, 58.7, 7, brand="Feldmühle")
        FoodUnit.objects.create(food=cls.oats, kind=FoodUnit.Kind.PORTION, amount=40)
        FoodUnit.objects.create(food=cls.oats, kind=FoodUnit.Kind.TABLESPOON, amount=10)
        cls.drink = food("Haferdrink", 59, 1, 6.6, 3, basis=Basis.MILLILITRE)
        cls.skyr = food("Skyr natur", 63, 11, 4, 0.2)

        cls.bowl = Meal.objects.create(owner=cls.user, name="Overnight Oats")
        MealItem.objects.create(meal=cls.bowl, food=cls.oats, amount=50)
        MealItem.objects.create(meal=cls.bowl, food=cls.skyr, amount=150)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def log_food(
        self, food=None, quantity=50, unit="g", section="fruehstueck", day=TODAY
    ):
        return self.client.post(
            "/diary/entries/",
            {
                "date": day.isoformat(),
                "section": section,
                "food": (food or self.oats).id,
                "quantity": quantity,
                "unit": unit,
            },
            format="json",
        )

    def log_meal(self, meal=None, servings=1, section="fruehstueck", day=TODAY):
        return self.client.post(
            "/diary/entries/",
            {
                "date": day.isoformat(),
                "section": section,
                "meal": (meal or self.bowl).id,
                "servings": servings,
            },
            format="json",
        )

    def day(self, day=TODAY):
        return self.client.get(f"/diary/days/{day.isoformat()}/").json()


class DiaryDayTests(TrackingTestCase):
    def test_requires_login(self):
        self.client.force_authenticate(None)

        response = self.client.get(f"/diary/days/{TODAY.isoformat()}/")

        self.assertIn(response.status_code, (401, 403))

    def test_empty_day_has_all_sections_in_order_and_the_goals(self):
        day = self.day()

        self.assertEqual(
            [(s["key"], s["name"]) for s in day["sections"]],
            [
                ("fruehstueck", "Frühstück"),
                ("mittagessen", "Mittagessen"),
                ("abendessen", "Abendessen"),
                ("snacks", "Snacks"),
                ("dessert", "Dessert"),
            ],
        )
        self.assertEqual(
            day["goals"], {"kcal": 2180, "protein": 140, "carbs": 245, "fat": 70}
        )
        self.assertEqual(day["totals"]["kcal"], 0)

    def test_without_calorie_target_there_are_no_goals(self):
        DailyGoal.objects.filter(owner=self.user).delete()

        self.assertIsNone(self.day()["goals"])

    def test_sections_and_day_sum_their_entries(self):
        self.log_food(quantity=50)
        self.log_food(food=self.drink, quantity=200, unit="ml")
        self.log_food(food=self.skyr, quantity=150, section="snacks")

        day = self.day()
        breakfast, snacks = day["sections"][0], day["sections"][3]

        self.assertEqual(len(breakfast["entries"]), 2)
        self.assertEqual(breakfast["totals"]["kcal"], 302.0)  # 184 + 118
        self.assertEqual(snacks["totals"]["kcal"], 94.5)
        self.assertEqual(day["totals"]["kcal"], 396.5)

    def test_impossible_date_is_not_found(self):
        response = self.client.get("/diary/days/2026-02-30/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LogFoodTests(TrackingTestCase):
    def test_food_entry_with_unit(self):
        response = self.log_food(quantity=1.5, unit="portion")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        entry = response.json()
        self.assertEqual(entry["kind"], "food")
        self.assertEqual(entry["name"], "Haferflocken, kernig")
        self.assertEqual(entry["brand"], "Feldmühle")
        self.assertEqual(entry["quantity"], 1.5)
        self.assertEqual(
            entry["unit"], {"key": "portion", "name": "Portion", "amount": 40.0}
        )
        self.assertEqual(
            entry["nutrients"],
            {"kcal": 220.8, "protein": 8.1, "carbs": 35.2, "fat": 4.2},
        )
        self.assertEqual(
            [unit["key"] for unit in entry["units"]], ["g", "portion", "tablespoon"]
        )
        self.assertEqual(entry["per100"]["kcal"], 368.0)
        self.assertEqual(entry["basis"], "g")
        self.assertIsNone(entry["servings"])

    def test_unit_defaults_to_the_basis(self):
        response = self.client.post(
            "/diary/entries/",
            {
                "date": TODAY.isoformat(),
                "section": "snacks",
                "food": self.drink.id,
                "quantity": 200,
            },
            format="json",
        )

        self.assertEqual(response.json()["unit"]["key"], "ml")

    def test_validation(self):
        cases = [
            ({"quantity": 0}, "quantity"),
            ({"quantity": None}, "quantity"),
            ({"unit": "slice"}, "unit"),
            ({"quantity": 300, "unit": "portion"}, "quantity"),  # 12 kg
            ({"section": "brunch"}, "section"),
            ({"date": (TODAY + timedelta(days=500)).isoformat()}, "date"),
        ]

        for overrides, field in cases:
            with self.subTest(overrides=overrides):
                payload = {
                    "date": TODAY.isoformat(),
                    "section": "fruehstueck",
                    "food": self.oats.id,
                    "quantity": 50,
                    "unit": "g",
                }
                payload.update(overrides)
                response = self.client.post("/diary/entries/", payload, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.json())

    def test_future_days_are_allowed_for_planning(self):
        response = self.log_food(day=TODAY + timedelta(days=3))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_needs_either_food_or_meal(self):
        response = self.client.post(
            "/diary/entries/",
            {"date": TODAY.isoformat(), "section": "snacks"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_values_stay_as_logged_when_the_food_changes(self):
        self.log_food(quantity=100)
        Food.objects.filter(pk=self.oats.pk).update(kcal_per_100=999)

        entry = self.day()["sections"][0]["entries"][0]

        self.assertEqual(entry["nutrients"]["kcal"], 368.0)


class LogMealTests(TrackingTestCase):
    def test_meal_entry_is_one_group_with_scaled_ingredients(self):
        response = self.log_meal(servings=1.5)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        entry = response.json()
        self.assertEqual(
            (entry["kind"], entry["name"], entry["servings"]),
            ("meal", "Overnight Oats", 1.5),
        )
        self.assertEqual(
            [(item["name"], item["amount"]) for item in entry["items"]],
            [("Haferflocken, kernig", 75.0), ("Skyr natur", 225.0)],
        )
        self.assertEqual(entry["perServing"]["kcal"], 278.5)  # 184 + 94.5
        self.assertEqual(entry["nutrients"]["kcal"], 417.8)
        self.assertIsNone(entry["unit"])

    def test_servings_in_half_steps_from_half_to_twenty(self):
        for servings in (0, 0.25, 0.7, 20.5, None):
            with self.subTest(servings=servings):
                response = self.log_meal(servings=servings)

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("servings", response.json())

    def test_other_users_meals_cannot_be_logged(self):
        foreign = Meal.objects.create(owner=self.other, name="Fremd")
        MealItem.objects.create(meal=foreign, food=self.oats, amount=10)

        response = self.log_meal(meal=foreign)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("meal", response.json())

    def test_logged_meal_keeps_its_ingredients_when_the_meal_changes(self):
        self.log_meal()
        self.bowl.items.all().delete()
        self.bowl.delete()

        entry = self.day()["sections"][0]["entries"][0]

        self.assertEqual(len(entry["items"]), 2)
        self.assertIsNone(entry["meal"])


class EditEntryTests(TrackingTestCase):
    def test_change_quantity_unit_and_section(self):
        entry_id = self.log_food(quantity=50).json()["id"]

        response = self.client.patch(
            f"/diary/entries/{entry_id}/",
            {"quantity": 2, "unit": "tablespoon", "section": "snacks"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        entry = response.json()
        self.assertEqual((entry["quantity"], entry["section"]), (2.0, "snacks"))
        self.assertEqual(entry["nutrients"]["kcal"], 73.6)

    def test_change_servings_of_a_meal(self):
        entry_id = self.log_meal().json()["id"]

        response = self.client.patch(
            f"/diary/entries/{entry_id}/", {"servings": 2}, format="json"
        )

        self.assertEqual(response.json()["nutrients"]["kcal"], 557.0)

    def test_meal_entries_have_no_quantity_and_foods_no_servings(self):
        meal_entry = self.log_meal().json()["id"]
        food_entry = self.log_food().json()["id"]

        meal_response = self.client.patch(
            f"/diary/entries/{meal_entry}/", {"quantity": 10}, format="json"
        )
        food_response = self.client.patch(
            f"/diary/entries/{food_entry}/", {"servings": 2}, format="json"
        )

        self.assertEqual(meal_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(food_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_and_undo(self):
        entry_id = self.log_food().json()["id"]

        removed = self.client.delete(f"/diary/entries/{entry_id}/")
        self.assertEqual(removed.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.day()["sections"][0]["entries"], [])

        restored = self.client.post(f"/diary/entries/{entry_id}/restore/")
        self.assertEqual(restored.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.day()["sections"][0]["entries"]), 1)

    def test_purge_deletes_removed_entries_after_the_undo_window(self):
        entry_id = self.log_food().json()["id"]
        self.client.delete(f"/diary/entries/{entry_id}/")
        DiaryEntry.objects.update(deleted_at=timezone.now() - timedelta(days=2))

        call_command("purge_deleted_entries", stdout=StringIO())

        self.assertFalse(DiaryEntry.objects.exists())

    def test_other_users_entries_are_not_found(self):
        entry_id = self.log_food().json()["id"]
        self.client.force_authenticate(self.other)

        for response in (
            self.client.patch(f"/diary/entries/{entry_id}/", {"quantity": 1}),
            self.client.delete(f"/diary/entries/{entry_id}/"),
            self.client.post(f"/diary/entries/{entry_id}/restore/"),
        ):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SummaryCalendarRecentTests(TrackingTestCase):
    def test_summary_counts_and_sums_per_section(self):
        self.log_meal()
        self.log_food(food=self.drink, quantity=200, unit="ml")

        response = self.client.get(f"/diary/days/{TODAY.isoformat()}/summary/")
        summary = response.json()

        self.assertEqual(
            summary["sections"][0],
            {"key": "fruehstueck", "name": "Frühstück", "count": 2, "kcal": 396.5},
        )
        self.assertEqual(summary["sections"][1]["count"], 0)
        self.assertEqual(summary["goals"]["kcal"], 2180)

    def test_calendar_lists_days_with_active_entries(self):
        first = date(TODAY.year, TODAY.month, 1)
        self.log_food(day=first)
        self.log_food(day=first)
        removed = self.log_food(day=first + timedelta(days=1)).json()["id"]
        self.client.delete(f"/diary/entries/{removed}/")

        response = self.client.get(
            "/diary/calendar/", {"monat": first.strftime("%Y-%m")}
        )

        self.assertEqual(response.json()["days"], [first.isoformat()])

    def test_calendar_validates_the_month(self):
        response = self.client.get("/diary/calendar/", {"monat": "2026-13"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recent_lists_different_foods_with_their_last_amount(self):
        self.log_food(quantity=30)
        self.log_food(food=self.drink, quantity=200, unit="ml")
        self.log_food(quantity=1, unit="portion")
        self.log_meal()  # meals are not part of "Zuletzt"

        recent = self.client.get("/diary/recent/").json()

        self.assertEqual(
            [(r["food"]["name"], r["quantity"], r["unit"]["key"]) for r in recent],
            [("Haferflocken, kernig", 1.0, "portion"), ("Haferdrink", 200.0, "ml")],
        )
        self.assertEqual(recent[0]["nutrients"]["kcal"], 147.2)


class MealApiTests(TrackingTestCase):
    def payload(self, **overrides):
        data = {
            "name": "Protein-Bowl",
            "items": [
                {"food": self.oats.id, "amount": 60},
                {"food": self.skyr.id, "amount": 250},
            ],
        }
        data.update(overrides)

        return data

    def test_list_shows_own_meals_with_nutrients(self):
        Meal.objects.create(owner=self.other, name="Fremd")

        meals = self.client.get("/meals/").json()

        self.assertEqual([meal["name"] for meal in meals], ["Overnight Oats"])
        self.assertEqual(meals[0]["nutrients"]["kcal"], 278.5)
        self.assertEqual(meals[0]["items"][0]["food"]["name"], "Haferflocken, kernig")

    def test_create_update_delete(self):
        created = self.client.post("/meals/", self.payload(), format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED, created.data)
        meal_id = created.json()["id"]

        updated = self.client.put(
            f"/meals/{meal_id}/",
            self.payload(name="Bowl", items=[{"food": self.skyr.id, "amount": 100}]),
            format="json",
        )
        self.assertEqual(updated.json()["name"], "Bowl")
        self.assertEqual(len(updated.json()["items"]), 1)

        deleted = self.client.delete(f"/meals/{meal_id}/")
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)

    def test_validation_messages(self):
        response = self.client.post(
            "/meals/", self.payload(name="", items=[]), format="json"
        )

        self.assertEqual(
            response.json(),
            {
                "name": ["Gib der Mahlzeit einen Namen."],
                "items": ["Füge mindestens ein Lebensmittel hinzu."],
            },
        )

    def test_other_users_meals_are_not_found(self):
        self.client.force_authenticate(self.other)

        response = self.client.get(f"/meals/{self.bowl.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class WeightApiTests(TrackingTestCase):
    def put(self, day, weight):
        return self.client.put(
            f"/weight/{day.isoformat()}/", {"weight": weight}, format="json"
        )

    def test_one_value_per_day_saving_replaces(self):
        first = self.put(TODAY, 78.6)
        second = self.put(TODAY, 78.4)

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(WeightEntry.objects.get().weight, Decimal("78.4"))

    def test_validation_messages(self):
        cases = [
            (None, "Gib dein Gewicht in Kilogramm ein, zum Beispiel 78,4."),
            (19.9, "Das Gewicht muss zwischen 20 und 400 kg liegen."),
            (400.1, "Das Gewicht muss zwischen 20 und 400 kg liegen."),
        ]

        for weight, message in cases:
            with self.subTest(weight=weight):
                response = self.put(TODAY, weight)

                self.assertEqual(response.json(), {"weight": [message]})

    def test_overview_of_a_period(self):
        end = date(2026, 10, 14)  # a Wednesday, ISO week 42
        for days_ago, weight in (
            (40, 80.0),
            (20, 79.6),
            (9, 79.0),
            (8, 78.8),
            (0, 78.4),
        ):
            self.put(end - timedelta(days=days_ago), weight)

        response = self.client.get(
            "/weight/", {"zeitraum": "30", "bis": end.isoformat()}
        )
        overview = response.json()

        self.assertEqual(overview["start"], "2026-09-15")
        self.assertEqual(
            [m["weight"] for m in overview["measurements"]], [79.6, 79.0, 78.8, 78.4]
        )
        self.assertEqual(overview["latest"], {"date": "2026-10-14", "weight": 78.4})
        self.assertEqual(
            overview["stats"],
            {
                "start": 79.6,
                "current": 78.4,
                "change": -1.2,
                "perWeek": -0.4,
                "count": 4,
            },
        )
        newest = overview["weeks"][0]
        self.assertEqual(
            (newest["week"], newest["start"], newest["end"], newest["isCurrent"]),
            (42, "2026-10-12", "2026-10-18", True),
        )
        self.assertEqual((newest["average"], newest["change"]), (78.4, -0.5))

    def test_whole_history_and_period_validation(self):
        self.put(date(2025, 1, 6), 82)
        self.put(TODAY, 80)

        whole = self.client.get("/weight/", {"zeitraum": "alle"}).json()
        invalid = self.client.get("/weight/", {"zeitraum": "14"})

        self.assertEqual(whole["stats"]["count"], 2)
        self.assertIsNone(whole["start"])
        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_overview(self):
        overview = self.client.get("/weight/").json()

        self.assertEqual(
            (overview["latest"], overview["stats"], overview["weeks"]), (None, None, [])
        )

    def test_delete_and_ownership(self):
        self.put(TODAY, 78)
        self.client.force_authenticate(self.other)
        foreign = self.client.delete(f"/weight/{TODAY.isoformat()}/")
        self.client.force_authenticate(self.user)
        own = self.client.delete(f"/weight/{TODAY.isoformat()}/")

        self.assertEqual(foreign.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(own.status_code, status.HTTP_204_NO_CONTENT)


class WeightCalculationTests(APITestCase):
    def entry(self, day, weight):
        return WeightEntry(date=day, weight=Decimal(str(weight)))

    def test_week_change_needs_the_calendar_week_before(self):
        entries = [
            self.entry(date(2026, 9, 28), 80),  # KW 40
            self.entry(date(2026, 10, 12), 79),  # KW 42, KW 41 empty
        ]

        weeks = weeks_of(entries, None, date(2026, 10, 14), date(2026, 10, 14))

        self.assertEqual([w["week"] for w in weeks], [42, 40])
        self.assertIsNone(weeks[0]["change"])

    def test_tempo_needs_at_least_a_week(self):
        short = stats_of(
            [self.entry(date(2026, 10, 1), 80), self.entry(date(2026, 10, 4), 79)]
        )

        self.assertIsNone(short["per_week"])


class ConsentTests(TrackingTestCase):
    def test_revoking_deletes_health_data_but_keeps_meals(self):
        self.log_food()
        self.client.put(f"/weight/{TODAY.isoformat()}/", {"weight": 78}, format="json")
        BodyData.objects.create(owner=self.user, height=172)

        response = self.client.delete("/profile/consent/")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertFalse(response.data["granted"])
        self.assertFalse(DiaryEntry.objects.filter(owner=self.user).exists())
        self.assertFalse(WeightEntry.objects.filter(owner=self.user).exists())
        self.assertFalse(DailyGoal.objects.filter(owner=self.user).exists())
        self.assertFalse(BodyData.objects.filter(owner=self.user).exists())
        self.assertTrue(Meal.objects.filter(owner=self.user).exists())

    def test_status_counts_what_a_revocation_deletes(self):
        self.log_food()
        self.log_food()
        removed = self.log_food().data["id"]
        self.client.delete(f"/diary/entries/{removed}/")
        self.client.put(f"/weight/{TODAY.isoformat()}/", {"weight": 78}, format="json")

        deletes = self.client.get("/profile/consent/").data["deletes"]

        self.assertEqual(deletes["diary_entries"], 2)
        self.assertEqual(deletes["weight_entries"], 1)

    def test_writes_without_consent_are_refused_with_a_code(self):
        self.client.force_authenticate(self.stranger)
        today = TODAY.isoformat()

        responses = [
            self.client.post(
                "/diary/entries/",
                {
                    "date": today,
                    "section": "snacks",
                    "food": self.oats.id,
                    "quantity": 1,
                    "unit": "g",
                },
                format="json",
            ),
            self.client.put(f"/weight/{today}/", {"weight": 78}, format="json"),
            self.client.put("/goals/", self.goal_payload(), format="json"),
        ]

        for response in responses:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(response.json()["code"], "consent_required")

    def test_reads_and_meals_work_without_consent(self):
        self.client.force_authenticate(self.stranger)

        self.assertEqual(self.client.get("/goals/").status_code, status.HTTP_200_OK)
        response = self.client.post(
            "/meals/",
            {"name": "Müsli", "items": [{"food": self.oats.id, "amount": 50}]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_granting_stores_time_and_version(self):
        self.client.force_authenticate(self.stranger)

        response = self.client.post("/profile/consent/")

        self.assertTrue(response.data["granted"])
        self.assertEqual(response.data["version"], 1)
        self.assertIsNotNone(response.data["granted_at"])

    def test_consent_cannot_change_through_the_profile(self):
        self.client.patch("/profile/", {"dataConsent": False}, format="json")

        self.assertTrue(Profile.objects.get(user=self.user).data_consent)

    def test_profile_cannot_be_moved_to_another_user(self):
        self.client.patch("/profile/", {"user": self.other.id}, format="json")

        self.assertEqual(Profile.objects.get(user=self.user).user, self.user)

    def goal_payload(self, kcal=2000, **extra):
        return {
            "goal": {
                "source": "berechnet",
                "kcal": kcal,
                "protein": 130,
                "carbs": 220,
                "fat": 66,
                "weight": 78.4,
            },
            **extra,
        }


class GoalTests(TrackingTestCase):
    def save(self, kcal=2000, **extra):
        payload = {
            "goal": {
                "source": "berechnet",
                "kcal": kcal,
                "protein": 130,
                "carbs": 220,
                "fat": 66,
                "weight": 78.4,
            },
            **extra,
        }

        return self.client.put("/goals/", payload, format="json")

    def test_a_new_goal_applies_from_today_and_past_days_keep_theirs(self):
        response = self.save(kcal=2000)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["current"]["kcal"], 2000)
        self.assertEqual(response.data["previous"]["kcal"], 2180)
        self.assertEqual(self.day()["goals"]["kcal"], 2000)
        self.assertEqual(self.day(TODAY - timedelta(days=1))["goals"]["kcal"], 2180)
        self.assertIsNone(self.day(TODAY - timedelta(days=31))["goals"])

    def test_the_newest_version_of_a_day_applies(self):
        self.save(kcal=2000)
        self.save(kcal=2100)

        self.assertEqual(self.day()["goals"]["kcal"], 2100)
        self.assertEqual(self.client.get("/goals/").data["previous"]["kcal"], 2180)

    def test_a_calculated_goal_stays_available_after_a_custom_one(self):
        self.save(kcal=2000)
        self.client.put(
            "/goals/",
            {
                "goal": {
                    "source": "eigener-wert",
                    "kcal": 1900,
                    "protein": 140,
                    "carbs": 200,
                    "fat": 60,
                }
            },
            format="json",
        )

        data = self.client.get("/goals/").data

        self.assertEqual(data["current"]["kcal"], 1900)
        self.assertEqual(data["last_calculated"]["kcal"], 2000)

    def test_inputs_and_weight_are_saved_with_the_goal(self):
        body = {
            "sex": "female",
            "age": 32,
            "height": 172,
            "steps": 8000,
            "workouts": [{"met": "1-2-4.5", "duration": 60, "frequency": 3}],
            "goal": "diet",
        }

        response = self.save(body=body, recordWeight=True)

        self.assertEqual(response.data["body"], body)
        self.assertEqual(response.data["latest_weight"]["weight"], Decimal("78.4"))
        self.assertTrue(
            WeightEntry.objects.filter(owner=self.user, date=TODAY).exists()
        )

    def test_without_record_weight_no_measurement_is_written(self):
        self.save(recordWeight=False)

        self.assertFalse(WeightEntry.objects.filter(owner=self.user).exists())

    def test_age_grows_with_the_years(self):
        body = BodyData(age=32, age_given_on=date(2024, 10, 15))

        self.assertEqual(body.current_age(date(2026, 10, 14)), 33)
        self.assertEqual(body.current_age(date(2026, 10, 15)), 34)

    def test_the_minimum_and_the_weight_are_checked(self):
        response = self.save(kcal=500)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("kcal", response.data["goal"])

    def test_a_weight_change_of_two_kilos_is_pointed_out(self):
        WeightEntry.objects.create(owner=self.user, date=TODAY, weight=Decimal("76.4"))

        self.assertEqual(
            self.client.get("/goals/").data["weight_change"], Decimal("-2.0")
        )

        WeightEntry.objects.filter(owner=self.user).update(weight=Decimal("77.0"))

        self.assertIsNone(self.client.get("/goals/").data["weight_change"])

    def test_custom_macros_are_kept_as_entered(self):
        payload = {
            "goal": {
                "source": "eigener-wert",
                "kcal": 2000,
                "protein": 160,
                "carbs": 150,
                "fat": 85,
                "customMacros": True,
            }
        }

        current = self.client.put("/goals/", payload, format="json").data["current"]

        self.assertTrue(current["custom_macros"])
        self.assertEqual(
            (current["protein"], current["carbs"], current["fat"]), (160, 150, 85)
        )

    def test_a_calculated_goal_cannot_have_custom_macros(self):
        payload = {
            "goal": {
                "source": "berechnet",
                "kcal": 2000,
                "protein": 130,
                "carbs": 220,
                "fat": 66,
                "customMacros": True,
            }
        }

        response = self.client.put("/goals/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("custom_macros", response.data["goal"])

    def test_a_far_off_today_is_refused(self):
        response = self.save(today=(TODAY + timedelta(days=3)).isoformat())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
