from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.exceptions import OnboardingStepNotAllowed
from apps.accounts.services import Step, go_to, is_allowed

from .serializers import OnboardingStateSerializer


class OnboardingView(generics.RetrieveAPIView):
    serializer_class = OnboardingStateSerializer

    def get_object(self):
        return self.request.user.profile

    def patch(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        step = serializer.validated_data["onboarding_step"]

        if not is_allowed(profile, step):
            raise OnboardingStepNotAllowed()

        go_to(profile, step)

        return Response(self.get_serializer(profile).data)


class OnboardingCompleteView(APIView):
    def post(self, request):
        profile = request.user.profile

        if profile.onboarding_completed or profile.onboarding_step != Step.SUMMARY:
            raise OnboardingStepNotAllowed(
                "Das Onboarding lässt sich erst in der Zusammenfassung abschließen."
            )

        profile.onboarding_completed = True
        profile.save(update_fields=["onboarding_completed"])

        return Response(OnboardingStateSerializer(profile).data)
