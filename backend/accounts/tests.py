from django.conf import settings
from django.contrib.auth import get_user_model
from recipes.models import Recipe
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken
from tracking.models import Meal

from accounts.models import Profile

PASSWORD = "kernig-haferflocken-42"


class AccountTestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="lena@example.de", password=PASSWORD, tos_accepted=True
        )
        Profile.objects.create(user=self.user)
        self.client.force_authenticate(self.user)


class ProfileTests(AccountTestCase):
    def test_profile_shows_email_consent_and_terms(self):
        data = self.client.get("/profile/").data

        self.assertEqual(data["email"], "lena@example.de")
        self.assertEqual(data["onboarding"], "offen")
        self.assertEqual(data["diet"], "alles")
        self.assertFalse(data["consent"]["granted"])
        self.assertIsNotNone(data["tos_accepted_at"])

    def test_name_is_required_once_given(self):
        response = self.client.patch("/profile/", {"name": "  "}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["name"], ["Gib deinen Namen ein."])

    def test_finishing_the_onboarding_forgets_the_step(self):
        self.client.patch(
            "/profile/", {"usage": "beides", "onboardingStep": "angaben"}, format="json"
        )

        data = self.client.patch(
            "/profile/", {"onboarding": "abgeschlossen"}, format="json"
        ).data

        self.assertEqual(data["usage"], "beides")
        self.assertEqual(data["onboarding_step"], "")

    def test_unknown_usage_is_refused(self):
        response = self.client.patch("/profile/", {"usage": "alles"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_cannot_be_changed_here(self):
        self.client.patch("/profile/", {"email": "neu@example.de"}, format="json")

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "lena@example.de")


class PasswordChangeTests(AccountTestCase):
    def login_cookie(self):
        token = RefreshToken.for_user(self.user)
        self.client.cookies[settings.AUTH_COOKIE["NAME"]] = str(token)

        return token

    def test_wrong_current_password_is_named(self):
        response = self.client.post(
            "/auth/password/",
            {"currentPassword": "falsch", "newPassword": "neues-passwort-17"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["current_password"], ["Das aktuelle Passwort stimmt nicht."]
        )

    def test_new_password_follows_the_rules(self):
        response = self.client.post(
            "/auth/password/",
            {"currentPassword": PASSWORD, "newPassword": "12345678"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)

    def test_other_sessions_end_and_this_one_stays(self):
        other_device = RefreshToken.for_user(self.user)
        this_device = self.login_cookie()

        response = self.client.post(
            "/auth/password/",
            {"currentPassword": PASSWORD, "newPassword": "neues-passwort-17"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("neues-passwort-17"))
        blacklisted = set(BlacklistedToken.objects.values_list("token__jti", flat=True))
        self.assertIn(other_device["jti"], blacklisted)
        self.assertNotIn(this_device["jti"], blacklisted)


class AccountDeleteTests(AccountTestCase):
    def test_wrong_password_keeps_the_account(self):
        response = self.client.post(
            "/auth/delete-account/", {"password": "falsch"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["password"], ["Das Passwort stimmt nicht."])
        self.assertTrue(get_user_model().objects.filter(pk=self.user.pk).exists())

    def test_deleting_removes_everything_and_ends_sessions(self):
        session = RefreshToken.for_user(self.user)
        Recipe.objects.create(
            owner=self.user,
            name="Porridge",
            protein_per_serving=10,
            carbs_per_serving=50,
            fat_per_serving=8,
            servings=1,
            duration_minutes=10,
        )
        Meal.objects.create(owner=self.user, name="Müsli")

        response = self.client.post(
            "/auth/delete-account/", {"password": PASSWORD}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(get_user_model().objects.filter(pk=self.user.pk).exists())
        self.assertFalse(Recipe.objects.filter(name="Porridge").exists())
        self.assertFalse(Meal.objects.filter(name="Müsli").exists())
        self.assertTrue(
            BlacklistedToken.objects.filter(token__jti=session["jti"]).exists()
        )
        self.assertEqual(response.cookies[settings.AUTH_COOKIE["NAME"]].value, "")


class ExportTests(AccountTestCase):
    def test_export_is_a_json_file_with_all_sections(self):
        Meal.objects.create(owner=self.user, name="Müsli")

        response = self.client.get("/profile/export/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("attachment", response["Content-Disposition"])
        data = response.json()
        self.assertEqual(data["account"]["email"], "lena@example.de")
        for section in ("profile", "dailyGoals", "diary", "weight", "meals", "recipes"):
            self.assertIn(section, data)
        self.assertEqual(data["meals"][0]["name"], "Müsli")
