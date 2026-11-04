from datetime import date, timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.accounts.models import BodyProfile
from config.testing import ApiTestCase


class BodyProfileTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.create_user(username="gurke", consent=True)
        self.login(self.user)

    def test_empty_until_something_is_saved(self):
        response = self.client.get(reverse("body"))

        self.assertEqual(
            response.data, {"birth_date": None, "height_cm": None, "sex": None}
        )

    def test_fields_are_saved_one_by_one(self):
        self.client.patch(reverse("body"), {"birth_date": "1990-05-17"})
        self.client.patch(reverse("body"), {"height_cm": 172})
        response = self.client.patch(reverse("body"), {"sex": "male"})

        self.assertEqual(
            response.data,
            {"birth_date": "1990-05-17", "height_cm": 172, "sex": "male"},
        )
        self.assertEqual(self.client.get(reverse("body")).data, response.data)

    def test_null_clears_a_field(self):
        self.client.patch(reverse("body"), {"height_cm": 172, "sex": "male"})

        response = self.client.patch(reverse("body"), {"height_cm": None})

        self.assertEqual(response.data["height_cm"], None)
        self.assertEqual(response.data["sex"], "male")

    def test_limits_match_the_calorie_calculator(self):
        today = timezone.localdate()
        too_young = date(today.year - 10, 1, 1).isoformat()

        response = self.client.patch(
            reverse("body"),
            {"birth_date": too_young, "height_cm": 300, "sex": "divers"},
        )

        errors = response.data["errors"]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(errors), {"birth_date", "height_cm", "sex"})
        self.assertFalse(BodyProfile.objects.exists())

    def test_minimum_age_is_16(self):
        today = timezone.localdate()
        # One day short of 16, and 16 today
        fifteen = date(today.year - 16, today.month, today.day) + timedelta(days=1)
        sixteen = date(today.year - 16, today.month, today.day)

        too_young = self.client.patch(
            reverse("body"), {"birth_date": fifteen.isoformat()}
        )
        old_enough = self.client.patch(
            reverse("body"), {"birth_date": sixteen.isoformat()}
        )

        self.assertEqual(too_young.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("birth_date", too_young.data["errors"])
        self.assertEqual(old_enough.status_code, status.HTTP_200_OK)
        self.assertEqual(old_enough.data["birth_date"], sixteen.isoformat())

    def test_body_data_needs_consent(self):
        self.user.profile.consent_accepted = False
        self.user.profile.save()

        read = self.client.get(reverse("body"))
        write = self.client.patch(reverse("body"), {"height_cm": 172})

        self.assertEqual(read.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(write.data["code"], "consent_required")
        self.assertFalse(BodyProfile.objects.exists())

    def test_body_data_goes_with_the_account(self):
        self.client.patch(reverse("body"), {"height_cm": 172})

        self.user.delete()

        self.assertFalse(BodyProfile.objects.exists())
