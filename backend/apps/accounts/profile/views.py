from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import BodyProfile
from apps.accounts.permissions import HasPrivacyConsent
from apps.accounts.services import Step, advance

from .serializers import (
    EMPTY_BODY_PROFILE,
    BodyProfileSerializer,
    ProfileSerializer,
)


class ProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.profile

    def patch(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        advance(profile, Step.USERNAME, Step.CONSENT)

        return Response(serializer.data)


class BodyProfileView(APIView):
    """Date of birth, height and sex; health data, so only with consent."""

    permission_classes = [IsAuthenticated, HasPrivacyConsent]

    def get(self, request):
        body = BodyProfile.objects.filter(profile=request.user.profile).first()

        if body is None:
            return Response(EMPTY_BODY_PROFILE)

        return Response(BodyProfileSerializer(body).data)

    def patch(self, request):
        """Changes the given fields only; null clears one."""
        profile = request.user.profile
        body = BodyProfile.objects.filter(profile=profile).first()
        serializer = BodyProfileSerializer(body, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        body = serializer.save(profile=profile)

        return Response(BodyProfileSerializer(body).data)
