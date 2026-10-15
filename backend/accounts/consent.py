"""Granting and withdrawing the consent to store health data.

Health data are body data, daily goals, the diary and the weight history. The
apps that store them refuse writes without consent (HealthDataConsent) and
delete everything in a receiver of health_data_consent_revoked.
"""

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import Profile
from .signals import health_data_consent_revoked, health_data_summary


def grant(profile):
    if profile.data_consent:
        return profile

    profile.data_consent = True
    profile.data_consent_date_granted = timezone.now()
    profile.data_consent_date_revoked = None
    profile.data_consent_version = settings.SENSITIVE_DATA_CONSENT_VERSION
    profile.save(
        update_fields=[
            "data_consent",
            "data_consent_date_granted",
            "data_consent_date_revoked",
            "data_consent_version",
        ]
    )

    return profile


@transaction.atomic
def revoke(profile):
    """Withdraws the consent and deletes the health data for good, in one go."""
    if profile.data_consent:
        profile.data_consent = False
        profile.data_consent_date_revoked = timezone.now()
        profile.save(update_fields=["data_consent", "data_consent_date_revoked"])

    health_data_consent_revoked.send(sender=Profile, user=profile.user)

    return profile


def summary(user):
    """What a revocation would delete, e.g. {"diary_entries": 142, …}."""
    counts = {}

    for _receiver, response in health_data_summary.send(sender=Profile, user=user):
        counts.update(response or {})

    return counts
