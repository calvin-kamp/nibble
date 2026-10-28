from django.db import transaction
from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response

from accounts.models import ConsentRecord
from accounts.services.onboarding import after_consent_decision
from tracking.services import delete_tracking_data

from .serializers import ConsentDecisionSerializer, ConsentStateSerializer


class ConsentView(generics.RetrieveAPIView):
    serializer_class = ConsentStateSerializer

    def get_object(self):
        return self.request.user.profile

    def put(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = ConsentDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        accepted = serializer.validated_data["accepted"]
        policy_version = serializer.validated_data["policy_version"]
        revoked = profile.has_consent and not accepted
        decided_at = timezone.now()

        with transaction.atomic():
            profile.consent_accepted = accepted
            profile.consent_decided_at = decided_at
            profile.consent_policy_version = policy_version
            profile.save(
                update_fields=[
                    "consent_accepted",
                    "consent_decided_at",
                    "consent_policy_version",
                ]
            )

            # Every decision is added to the history, revocations included.
            ConsentRecord.objects.create(
                profile=profile,
                accepted=accepted,
                policy_version=policy_version,
                decided_at=decided_at,
            )

            # Revoking deletes all tracking data right away and for good.
            if revoked:
                delete_tracking_data(profile)

            after_consent_decision(profile)

        return Response(ConsentStateSerializer(profile).data)
