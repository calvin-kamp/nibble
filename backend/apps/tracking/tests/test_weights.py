from datetime import date, timedelta
from decimal import Decimal

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.tracking.models import WeightEntry
from config.testing import ApiTestCase


class WeightTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.create_user(username="gurke", consent=True)
        self.login(self.user)
        self.today = timezone.localdate()

    def add(self, day, weight):
        return WeightEntry.objects.create(
            profile=self.user.profile, measured_on=day, weight_kg=Decimal(str(weight))
        )

    def test_one_entry_per_day(self):
        payload = {"weight_kg": 80.5, "measured_on": str(self.today)}

        first = self.client.post(reverse("weights"), payload)
        second = self.client.post(reverse("weights"), payload)
        imprecise = self.client.post(
            reverse("weights"), {"weight_kg": 80.55, "measured_on": "2026-01-01"}
        )

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(first.data["weight_kg"], Decimal("80.5"))
        self.assertEqual(second.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(second.data["code"], "weight_entry_exists")
        self.assertIn("weight_kg", imprecise.data["errors"])

    def test_patch_onto_another_day_is_a_conflict(self):
        self.add(self.today, 80)
        other = self.add(self.today - timedelta(days=1), 81)

        moved = self.client.patch(
            reverse("weight_detail", kwargs={"pk": other.pk}),
            {"measured_on": str(self.today)},
        )
        changed = self.client.patch(
            reverse("weight_detail", kwargs={"pk": other.pk}), {"weight_kg": 79.9}
        )

        self.assertEqual(moved.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(changed.data["weight_kg"], Decimal("79.9"))

    def test_range(self):
        for days_ago in (0, 6, 7, 40):
            self.add(self.today - timedelta(days=days_ago), 80)

        week = self.client.get(reverse("weights")).data
        everything = self.client.get(reverse("weights"), {"range": "all"}).data
        invalid = self.client.get(reverse("weights"), {"range": "2w"})

        self.assertEqual(len(week["results"]), 2)
        self.assertEqual(week["from"], self.today - timedelta(days=6))
        self.assertEqual(len(everything["results"]), 4)
        self.assertEqual(everything["from"], self.today - timedelta(days=40))
        self.assertIn("range", invalid.data["errors"])

    def test_weeks_compare_with_the_last_week_with_entries(self):
        # 2026-W01 starts on Monday 2025-12-29.
        self.add(date(2025, 12, 29), 80)
        self.add(date(2025, 12, 31), 81)
        # W02 has no entries, W03:
        self.add(date(2026, 1, 12), 80)
        # W04:
        self.add(date(2026, 1, 19), 80)

        weeks = self.client.get(reverse("weight_weeks")).data["results"]

        self.assertEqual(
            [(w["iso_year"], w["iso_week"]) for w in weeks],
            [(2026, 4), (2026, 3), (2026, 1)],
        )
        self.assertEqual(weeks[0]["trend"], "same")
        self.assertEqual(weeks[1]["change_kg"], -0.5)
        self.assertEqual(weeks[1]["trend"], "down")
        self.assertIsNone(weeks[2]["change_kg"])
        self.assertEqual(weeks[2]["average_kg"], Decimal("80.5"))
        self.assertEqual(weeks[2]["week_start"], "2025-12-29")

    def test_weeks_are_paged_by_before(self):
        monday = date(2026, 1, 5)

        for week in range(7):
            self.add(monday + timedelta(weeks=week), 80 + week)

        first = self.client.get(reverse("weight_weeks")).data
        rest = self.client.get(
            reverse("weight_weeks"), {"before": first["next_before"]}
        ).data
        invalid = self.client.get(reverse("weight_weeks"), {"before": "2026-W99"})

        # W02 to W08, five per page
        self.assertEqual(len(first["results"]), 5)
        self.assertEqual(first["next_before"], "2026-W04")
        self.assertEqual(first["total_weeks"], 7)
        self.assertEqual([w["iso_week"] for w in rest["results"]], [3, 2])
        self.assertIsNone(rest["next_before"])
        self.assertEqual(rest["total_weeks"], 7)
        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weeks_in_a_range(self):
        monday = date(2026, 1, 5)

        for week in range(7):
            self.add(monday + timedelta(weeks=week), 80 + week)

        # From Sunday of W02 to Monday of W04: the weeks that share a day with it
        weeks = self.client.get(
            reverse("weight_weeks"), {"from": "2026-01-11", "to": "2026-01-19"}
        ).data
        reversed_range = self.client.get(
            reverse("weight_weeks"), {"from": "2026-01-19", "to": "2026-01-11"}
        )
        invalid = self.client.get(reverse("weight_weeks"), {"from": "gestern"})

        self.assertEqual([w["iso_week"] for w in weeks["results"]], [4, 3, 2])
        self.assertEqual(weeks["total_weeks"], 3)
        self.assertIsNone(weeks["next_before"])
        # The comparison still uses the week before the range
        self.assertEqual(weeks["results"][2]["change_kg"], None)
        self.assertEqual(weeks["results"][0]["change_kg"], 1)
        self.assertIn("to", reversed_range.data["errors"])
        self.assertIn("from", invalid.data["errors"])

    def test_week_detail(self):
        self.add(date(2026, 1, 5), 80)
        self.add(date(2026, 1, 12), 81)
        self.add(date(2026, 1, 14), 82)

        detail = self.client.get(
            reverse("weight_week_detail", kwargs={"iso_year": 2026, "iso_week": 3})
        ).data
        empty = self.client.get(
            reverse("weight_week_detail", kwargs={"iso_year": 2026, "iso_week": 10})
        )
        # 2027 has only 52 ISO weeks.
        invalid = self.client.get(
            reverse("weight_week_detail", kwargs={"iso_year": 2027, "iso_week": 53})
        )

        self.assertEqual(detail["average_kg"], Decimal("81.5"))
        self.assertEqual(detail["change_kg"], Decimal("1.5"))
        self.assertEqual(detail["trend"], "up")
        self.assertEqual(
            detail["previous_week"],
            {"iso_year": 2026, "iso_week": 2, "average_kg": 80.0},
        )
        self.assertEqual([e["weight_kg"] for e in detail["entries"]], [81.0, 82.0])
        self.assertEqual(empty.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)
