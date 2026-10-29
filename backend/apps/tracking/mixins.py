from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import HasPrivacyConsent


class TrackingMixin:
    """All tracking endpoints need login and a given privacy consent."""

    permission_classes = [IsAuthenticated, HasPrivacyConsent]

    @property
    def profile(self):
        return self.request.user.profile
