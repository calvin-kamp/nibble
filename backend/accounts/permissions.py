from rest_framework.permissions import BasePermission


class HasPrivacyConsent(BasePermission):
    """Everything under /tracking/ needs a given privacy consent."""

    message = "Für das Tracking brauchst du eine Datenschutzeinwilligung."
    code = "consent_required"

    def has_permission(self, request, view):
        return request.user.profile.has_consent
