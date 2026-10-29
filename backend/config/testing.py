import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APIClient, APITestCase

from apps.accounts.models import User

from .celery import app as celery_app

PASSWORD = "Gurkensalat-2026"

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    MEDIA_ROOT=MEDIA_ROOT,
    SECURE_SSL_REDIRECT=False,
)
class ApiTestCase(APITestCase):
    """Clean rate limits, temporary media, e-mails sent right away (with on_commit).

    The test client speaks http, so the HTTPS redirect is off whatever .env says.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # With the CELERY namespace the prefixed key wins over task_always_eager.
        celery_app.conf.CELERY_TASK_ALWAYS_EAGER = True

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()

    @staticmethod
    def create_user(email="user@example.com", *, username=None, consent=None, **extra):
        user = User.objects.create_user(email, PASSWORD, **extra)
        profile = user.profile
        profile.username = username
        profile.consent_accepted = consent
        profile.save()

        return user

    def login(self, user):
        self.client.force_authenticate(user)

    @staticmethod
    def csrf_client():
        """Client that enforces CSRF like a browser, for the cookie flow tests."""
        return APIClient(enforce_csrf_checks=True)

    @staticmethod
    def access_cookie():
        return settings.AUTH_COOKIE["ACCESS_NAME"]
