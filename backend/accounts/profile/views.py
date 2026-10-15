from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts import consent
from accounts.models import Profile
from accounts.signals import personal_data_export

from .serializers import ConsentStatusSerializer, ProfileSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user.profile


class ConsentView(APIView):
    """GET status and what a revocation deletes, POST grants, DELETE revokes.

    Revoking deletes body data, daily goals, diary and weight history at once;
    account, recipes and own meals stay.
    """

    def status(self, profile):
        profile.deletes = consent.summary(profile.user)

        return Response(ConsentStatusSerializer(profile).data)

    def get(self, request):
        return self.status(request.user.profile)

    def post(self, request):
        return self.status(consent.grant(request.user.profile))

    def delete(self, request):
        return self.status(consent.revoke(request.user.profile))


class ExportView(APIView):
    """GET /profile/export/ – everything stored about the account, as a JSON file."""

    def get(self, request):
        user = request.user
        profile = user.profile
        data = {
            "exported_at": timezone.now(),
            "account": {
                "email": user.email,
                "date_joined": user.date_joined,
                "tos_accepted_at": user.tos_accepted_date,
                "tos_version": user.tos_version,
            },
            "profile": {
                "name": profile.name,
                "usage": profile.usage,
                "diet": profile.diet,
                "onboarding": profile.onboarding,
                "health_data_consent": {
                    "granted": profile.data_consent,
                    "granted_at": profile.data_consent_date_granted,
                    "revoked_at": profile.data_consent_date_revoked,
                    "version": profile.data_consent_version,
                },
            },
        }

        for _receiver, response in personal_data_export.send(sender=Profile, user=user):
            data.update(response or {})

        filename = f"nibble-daten-{timezone.localdate().isoformat()}.json"

        return Response(
            data,
            status=status.HTTP_200_OK,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
