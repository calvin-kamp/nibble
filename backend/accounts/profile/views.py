from django.db import IntegrityError, transaction
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.exceptions import UsernameTaken
from accounts.models import Profile
from accounts.services.onboarding import Step, advance

from .serializers import ProfileSerializer, UsernameQuerySerializer
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
