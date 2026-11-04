from django.conf import settings
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.accounts.models import User
from config.testing import PASSWORD, ApiTestCase

from .test_utils import link_token


class CookieAuthTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.client = self.csrf_client()
        token = self.client.get(reverse("csrf")).data["csrf_token"]
        self.client.credentials(HTTP_X_CSRFTOKEN=token)

    def register(self, email="neu@example.com", password=PASSWORD, **extra):
        data = {
            "email": email,
            "password": password,
            "terms_accepted": True,
            **extra,
        }

        return self.client.post(reverse("register"), data)

    def test_writes_need_the_csrf_header(self):
        self.client.credentials()

        response = self.register()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["code"], "csrf_failed")

    def test_register_logs_in_and_sends_verification(self):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.register("Neu@Example.com")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        data = response.data
        self.assertEqual(data["email"], "neu@example.com")
        self.assertFalse(data["email_verified"])
        self.assertIsNone(data["username"])
        self.assertIsNone(data["privacy_consent"])
        self.assertEqual(
            data["onboarding"], {"completed": False, "current_step": "username"}
        )

        refresh_cookie = response.cookies[settings.AUTH_COOKIE["REFRESH_NAME"]]
        self.assertTrue(refresh_cookie["httponly"])
        self.assertEqual(refresh_cookie["path"], settings.AUTH_COOKIE["REFRESH_PATH"])
        self.assertIn(self.access_cookie(), response.cookies)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(self.client.get(reverse("current_account")).status_code, 200)

    def test_register_stores_terms_acceptance(self):
        before = timezone.now()

        response = self.register()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        profile = User.objects.get(email="neu@example.com").profile
        self.assertGreaterEqual(profile.terms_accepted_at, before)
        self.assertEqual(profile.terms_version, settings.TERMS_VERSION)
        self.assertEqual(
            profile.privacy_policy_version, settings.PRIVACY_POLICY_VERSION
        )

    def test_register_needs_terms_accepted(self):
        declined = self.register(terms_accepted=False)
        missing = self.client.post(
            reverse("register"),
            {
                "email": "neu@example.com",
                "password": PASSWORD,
            },
        )

        for response in (declined, missing):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.data["errors"]["terms_accepted"],
                [
                    "Stimme den AGB zu und bestätige, dass du mindestens 16 Jahre alt bist."
                ],
            )
        self.assertFalse(User.objects.exists())

    def test_register_twice_is_a_conflict(self):
        self.register()
        response = self.register("NEU@example.com")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["code"], "email_taken")

    def test_register_rejects_weak_password(self):
        response = self.register(password="12345678")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response.data
        self.assertEqual(body["code"], "validation_error")
        self.assertIn("password", body["errors"])

    def test_login_with_wrong_password(self):
        self.create_user()

        response = self.client.post(
            reverse("login"), {"email": "user@example.com", "password": "falsch"}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["code"], "invalid_credentials")

    def test_login_is_rate_limited(self):
        for _ in range(5):
            self.client.post(
                reverse("login"), {"email": "x@example.com", "password": "x"}
            )

        response = self.client.post(
            reverse("login"), {"email": "x@example.com", "password": "x"}
        )

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response.data["code"], "throttled")
        self.assertIn("Retry-After", response.headers)

    def test_me_without_login(self):
        response = self.client.get(reverse("current_account"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["code"], "not_authenticated")

    def test_refresh_rotates_and_blocks_the_old_token(self):
        self.register()
        old_refresh = self.client.cookies[settings.AUTH_COOKIE["REFRESH_NAME"]].value

        first = self.client.post(reverse("token_refresh"))
        new_refresh = first.cookies[settings.AUTH_COOKIE["REFRESH_NAME"]].value
        self.client.cookies[settings.AUTH_COOKIE["REFRESH_NAME"]] = old_refresh
        second = self.client.post(reverse("token_refresh"))

        self.assertEqual(first.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotEqual(new_refresh, old_refresh)
        self.assertEqual(second.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_blocks_refresh_and_clears_cookies(self):
        self.register()
        refresh = self.client.cookies[settings.AUTH_COOKIE["REFRESH_NAME"]].value

        response = self.client.post(reverse("logout"))
        self.client.cookies[settings.AUTH_COOKIE["REFRESH_NAME"]] = refresh

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.cookies[self.access_cookie()].value, "")
        self.assertEqual(
            self.client.post(reverse("token_refresh")).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_email_verification(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.register()

        token = link_token(mail.outbox[0])
        response = self.client.post(reverse("email_verify"), {"token": token})
        invalid = self.client.post(reverse("email_verify"), {"token": token + "x"})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(User.objects.get(email="neu@example.com").email_verified)
        self.assertEqual(invalid.data["code"], "invalid_token")
        self.assertEqual(
            self.client.post(reverse("email_verification_resend")).data["code"],
            "already_verified",
        )

    def test_password_change_logs_out_other_sessions(self):
        self.register()
        other_session = self.client.cookies[settings.AUTH_COOKIE["REFRESH_NAME"]].value

        wrong = self.client.post(
            reverse("password_change"),
            {"current_password": "falsch", "new_password": "Neues-Passwort-42"},
        )
        response = self.client.post(
            reverse("password_change"),
            {"current_password": PASSWORD, "new_password": "Neues-Passwort-42"},
        )

        self.assertIn("current_password", wrong.data["errors"])
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get(reverse("current_account")).status_code, 200)

        self.client.cookies[settings.AUTH_COOKIE["REFRESH_NAME"]] = other_session
        self.assertEqual(
            self.client.post(reverse("token_refresh")).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_password_forgot_and_reset(self):
        self.create_user()

        with self.captureOnCommitCallbacks(execute=True):
            unknown = self.client.post(
                reverse("password_forgot"), {"email": "niemand@example.com"}
            )
            known = self.client.post(
                reverse("password_forgot"), {"email": "USER@example.com"}
            )

        self.assertEqual(unknown.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(known.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(mail.outbox), 1)

        token = link_token(mail.outbox[0])
        payload = {"token": token, "new_password": "Neues-Passwort-42"}
        reset = self.client.post(reverse("password_reset"), payload)
        reused = self.client.post(reverse("password_reset"), payload)

        self.assertEqual(reset.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(reused.data["code"], "invalid_token")
        self.assertTrue(
            User.objects.get(email="user@example.com").check_password(
                "Neues-Passwort-42"
            )
        )
