from rest_framework import serializers

from accounts.models import Profile


class ConsentSerializer(serializers.Serializer):
    granted = serializers.BooleanField(source="data_consent")
    granted_at = serializers.DateTimeField(source="data_consent_date_granted")
    version = serializers.IntegerField(source="data_consent_version")


class ProfileSerializer(serializers.ModelSerializer):
    """The account page and the start: name, usage, diet, onboarding, consent.

    The consent changes only through /profile/consent/, so that granting and
    withdrawing (with the deletion) can't happen as a side effect.
    """

    email = serializers.EmailField(source="user.email", read_only=True)
    tos_accepted_at = serializers.DateTimeField(
        source="user.tos_accepted_date", read_only=True
    )
    name = serializers.CharField(
        max_length=100,
        required=False,
        trim_whitespace=True,
        error_messages={"blank": "Gib deinen Namen ein."},
    )
    consent = ConsentSerializer(source="*", read_only=True)

    class Meta:
        model = Profile
        fields = (
            "email",
            "name",
            "usage",
            "diet",
            "onboarding",
            "onboarding_step",
            "consent",
            "tos_accepted_at",
        )
        extra_kwargs = {
            "usage": {
                "error_messages": {
                    "invalid_choice": "Wähle aus, wofür du Nibble nutzen möchtest."
                }
            },
        }

    def validate(self, attrs):
        # Finishing or skipping ends the onboarding; there's no step to resume.
        if attrs.get("onboarding", Profile.Onboarding.OPEN) != Profile.Onboarding.OPEN:
            attrs["onboarding_step"] = ""

        return attrs


class ConsentStatusSerializer(ConsentSerializer):
    revoked_at = serializers.DateTimeField(source="data_consent_date_revoked")
    # What a revocation would delete, for the confirmation dialog.
    deletes = serializers.DictField(child=serializers.IntegerField(), read_only=True)
