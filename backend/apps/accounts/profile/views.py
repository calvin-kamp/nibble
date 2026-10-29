from django.db import IntegrityError, transaction
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.exceptions import UsernameTaken
from apps.accounts.models import BodyProfile, Profile
from apps.accounts.permissions import HasPrivacyConsent
from apps.accounts.services import Step, advance

from .serializers import (
    EMPTY_BODY_PROFILE,
    BodyProfileSerializer,
    ProfileSerializer,
    UsernameQuerySerializer,
)
from .throttles import UsernameAvailabilityThrottle


def username_taken(username, profile):
    """Case-insensitive; the user's own current name counts as free."""
    return (
        Profile.objects.filter(username__iexact=username).exclude(pk=profile.pk).exists()
    )


class ProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.profile

    def patch(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)

        if username_taken(serializer.validated_data["username"], profile):
            raise UsernameTaken()

        try:
            with transaction.atomic():
                serializer.save()
        except IntegrityError as exc:
            raise UsernameTaken() from exc

        advance(profile, Step.USERNAME, Step.CONSENT)

        return Response(serializer.data)


class UsernameAvailabilityView(APIView):
    throttle_classes = [UsernameAvailabilityThrottle]

    def get(self, request):
        serializer = UsernameQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]

        return Response(
            {
                "username": username,
                "available": not username_taken(username, request.user.profile),
            }
        )


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
