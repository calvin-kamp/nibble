import re

from django.conf import settings
from django.core import mail
from rest_framework import status

from accounts.models import User
from config.testing import PASSWORD, ApiTestCase


def link_token(message):
    return re.search(r"token=(\S+)", message.body).group(1)


class CookieAuthTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.client = self.csrf_client()
        token = self.client.get("/auth/csrf").json()["csrf_token"]
        self.client.credentials(HTTP_X_CSRFTOKEN=token)

    def register(self, email="neu@example.com", password=PASSWORD):
        return self.client.post(
            "/auth/register", {"email": email, "password": password}
        )

    def test_writes_need_the_csrf_header(self):
        self.client.credentials()

        response = self.register()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["code"], "csrf_failed")

    def test_register_logs_in_and_sends_verification(self):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.register("Neu@Example.com")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        data = response.json()
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
        self.assertEqual(self.client.get("/auth/me").status_code, 200)

    def test_register_twice_is_a_conflict(self):
        self.register()
        response = self.register("NEU@example.com")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.json()["code"], "email_taken")

    def test_register_rejects_weak_password(self):
        response = self.register(password="12345678")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response.json()
        self.assertEqual(body["code"], "validation_error")
        self.assertIn("password", body["errors"])

    def test_login_with_wrong_password(self):
        self.create_user()

        response = self.client.post(
            "/auth/login", {"email": "user@example.com", "password": "falsch"}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["code"], "invalid_credentials")

    def test_login_is_rate_limited(self):
        for _ in range(5):
            self.client.post("/auth/login", {"email": "x@example.com", "password": "x"})

        response = self.client.post(
            "/auth/login", {"email": "x@example.com", "password": "x"}
        )

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response.json()["code"], "throttled")
        self.assertIn("Retry-After", response.headers)

    def test_me_without_login(self):
        response = self.client.get("/auth/me")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["code"], "not_authenticated")

    def test_refresh_rotates_and_blocks_the_old_token(self):
        self.register()
        old_refresh = self.client.cookies[settings.AUTH_COOKIE["REFRESH_NAME"]].value

        first = self.client.post("/auth/refresh")
        new_refresh = first.cookies[settings.AUTH_COOKIE["REFRESH_NAME"]].value
        self.client.cookies[settings.AUTH_COOKIE["REFRESH_NAME"]] = old_refresh
        second = self.client.post("/auth/refresh")

        self.assertEqual(first.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotEqual(new_refresh, old_refresh)
        self.assertEqual(second.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_blocks_refresh_and_clears_cookies(self):
        self.register()
        refresh = self.client.cookies[settings.AUTH_COOKIE["REFRESH_NAME"]].value

        response = self.client.post("/auth/logout")
        self.client.cookies[settings.AUTH_COOKIE["REFRESH_NAME"]] = refresh

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.cookies[self.access_cookie()].value, "")
        self.assertEqual(
            self.client.post("/auth/refresh").status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_email_verification(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.register()

        token = link_token(mail.outbox[0])
        response = self.client.post("/auth/email/verify", {"token": token})
        invalid = self.client.post("/auth/email/verify", {"token": token + "x"})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(User.objects.get(email="neu@example.com").email_verified)
        self.assertEqual(invalid.json()["code"], "invalid_token")
        self.assertEqual(
            self.client.post("/auth/email/verification/resend").json()["code"],
            "already_verified",
        )

    def test_password_change_logs_out_other_sessions(self):
        self.register()
        other_session = self.client.cookies[settings.AUTH_COOKIE["REFRESH_NAME"]].value

        wrong = self.client.post(
            "/auth/password/change",
            {"current_password": "falsch", "new_password": "Neues-Passwort-42"},
        )
        response = self.client.post(
            "/auth/password/change",
            {"current_password": PASSWORD, "new_password": "Neues-Passwort-42"},
        )

        self.assertIn("current_password", wrong.json()["errors"])
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get("/auth/me").status_code, 200)

        self.client.cookies[settings.AUTH_COOKIE["REFRESH_NAME"]] = other_session
        self.assertEqual(
            self.client.post("/auth/refresh").status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_password_forgot_and_reset(self):
        self.create_user()

        with self.captureOnCommitCallbacks(execute=True):
            unknown = self.client.post(
                "/auth/password/forgot", {"email": "niemand@example.com"}
            )
            known = self.client.post(
                "/auth/password/forgot", {"email": "USER@example.com"}
            )

        self.assertEqual(unknown.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(known.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(mail.outbox), 1)

        token = link_token(mail.outbox[0])
        payload = {"token": token, "new_password": "Neues-Passwort-42"}
        reset = self.client.post("/auth/password/reset", payload)
        reused = self.client.post("/auth/password/reset", payload)

        self.assertEqual(reset.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(reused.json()["code"], "invalid_token")
        self.assertTrue(
            User.objects.get(email="user@example.com").check_password(
                "Neues-Passwort-42"
            )
        )
