from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import CSRFCheck
from rest_framework.permissions import SAFE_METHODS
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


def enforce_csrf(request):
    """Same check as Django's CsrfViewMiddleware, which DRF skips for API views."""

    def dummy_get_response(request):
        return None

    check = CSRFCheck(dummy_get_response)
    check.process_request(request)
    reason = check.process_view(request, None, (), {})

    if reason:
        raise exceptions.PermissionDenied(
            "Die CSRF-Prüfung ist fehlgeschlagen. Lade die Seite neu.",
            code="csrf_failed",
        )


class CookieJWTAuthentication(JWTAuthentication):
    """Reads the access token from its HttpOnly cookie and enforces CSRF on writes.

    The browser sends the cookies on its own, so every unsafe request needs the
    CSRF header, logged in or not. An invalid or expired token counts as
    anonymous; protected endpoints then answer 401 and the frontend refreshes.
    """

    def authenticate(self, request):
        if request.method not in SAFE_METHODS:
            enforce_csrf(request)

        raw_token = request.COOKIES.get(settings.AUTH_COOKIE["ACCESS_NAME"])

        if not raw_token:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
        except (InvalidToken, exceptions.AuthenticationFailed):
            return None

        return user, validated_token

    def authenticate_header(self, request):
        # Without a header DRF would turn 401 into 403.
        return 'Cookie realm="api"'
