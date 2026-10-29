from rest_framework import serializers

from apps.accounts.models import Profile


class OnboardingStateSerializer(serializers.ModelSerializer):
    completed = serializers.BooleanField(source="onboarding_completed", read_only=True)
    current_step = serializers.ChoiceField(
        source="onboarding_step",
        choices=Profile.OnboardingStep,
    )

    class Meta:
        model = Profile
        fields = ("completed", "current_step")
