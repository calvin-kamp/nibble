from rest_framework.permissions import SAFE_METHODS, BasePermission

CONSENT_REQUIRED = "consent_required"


class HealthDataConsent(BasePermission):
    """Writes of health data need the consent; reads stay open (there's nothing
    to read without it).

    The response carries a stable code, so the frontend can ask for the consent
    and repeat the request, even when its own state is outdated.
    """

    message = {
        "code": CONSENT_REQUIRED,
        "detail": "Zum Speichern von Gesundheitsdaten braucht Nibble deine Einwilligung.",
    }

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        profile = getattr(request.user, "profile", None)

        return bool(profile and profile.data_consent)
