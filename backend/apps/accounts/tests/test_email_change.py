from datetime import timedelta

from django.core import mail
from django.test import override_settings
from rest_framework import status

from apps.accounts.models import User
from apps.accounts.tests.test_utils import link_token
from apps.accounts.tokens import make_email_change_token, make_verification_token
from config.testing import PASSWORD, ApiTestCase


class EmailChangeTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.create_user("alt@example.com", email_verified=True)
        self.login(self.user)

    def request_change(self, email="Neu@Example.com", password=PASSWORD):
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(
                "/auth/email/change", {"email": email, "password": password}
            )

    def confirm(self, token):
        return self.client.post("/auth/email/change/confirm", {"token": token})

    def test_link_goes_to_the_new_address_notice_to_the_old_one(self):
        response = self.request_change()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            sorted(message.to[0] for message in mail.outbox),
            ["alt@example.com", "neu@example.com"],
        )

        notice = next(m for m in mail.outbox if m.to == ["alt@example.com"])
        self.assertIn("neu@example.com", notice.body)
        self.assertNotIn("token=", notice.body)

    def test_address_only_changes_after_the_click(self):
        self.request_change()
        self.user.refresh_from_db()

        self.assertEqual(self.user.email, "alt@example.com")

        link = next(m for m in mail.outbox if m.to == ["neu@example.com"])
        self.client.logout()
        response = self.confirm(link_token(link))
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user.email, "neu@example.com")
        self.assertTrue(self.user.email_verified)
        self.assertEqual(self.confirm(link_token(link)).status_code, 204)

    def test_unverified_account_gets_no_notice(self):
        self.user.email_verified = False
        self.user.save()

        self.request_change()

        self.assertEqual([m.to for m in mail.outbox], [["neu@example.com"]])

    def test_needs_the_password(self):
        response = self.request_change(password="falsch")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.json()["errors"])
        self.assertEqual(mail.outbox, [])

    def test_rejects_taken_and_unchanged_addresses(self):
        self.create_user("vergeben@example.com")

        taken = self.request_change("Vergeben@example.com")
        same = self.request_change("ALT@example.com")

        self.assertIn("email", taken.json()["errors"])
        self.assertIn("email", same.json()["errors"])
        self.assertEqual(mail.outbox, [])

    def test_address_taken_before_the_click(self):
        token = make_email_change_token(self.user, "neu@example.com")
        self.create_user("neu@example.com")

        response = self.confirm(token)
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.json()["code"], "email_taken")
        self.assertEqual(self.user.email, "alt@example.com")

    def test_link_dies_when_the_address_changed_otherwise(self):
        first = make_email_change_token(self.user, "eins@example.com")
        second = make_email_change_token(self.user, "zwei@example.com")

        self.assertEqual(self.confirm(second).status_code, 204)
        response = self.confirm(first)

        self.assertEqual(response.json()["code"], "invalid_token")
        self.assertEqual(User.objects.get(pk=self.user.pk).email, "zwei@example.com")

    def test_old_verification_link_dies_with_the_old_address(self):
        verification = make_verification_token(self.user)

        self.confirm(make_email_change_token(self.user, "neu@example.com"))
        response = self.client.post("/auth/email/verify", {"token": verification})

        self.assertEqual(response.json()["code"], "invalid_token")

    @override_settings(EMAIL_CHANGE_MAX_AGE=timedelta(seconds=-1))
    def test_expired_link(self):
        response = self.confirm(make_email_change_token(self.user, "neu@example.com"))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["code"], "invalid_token")

    def test_needs_login(self):
        self.client.logout()

        response = self.request_change()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_is_rate_limited(self):
        for index in range(3):
            self.request_change(f"neu{index}@example.com")

        response = self.request_change("neu9@example.com")

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response.json()["code"], "throttled")
