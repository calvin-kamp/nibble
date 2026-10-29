from django.utils import timezone
from rest_framework import serializers

from apps.accounts.models import BodyProfile, Profile

USERNAME_PATTERN = r"^[A-Za-z0-9_]+$"


class UsernameField(serializers.RegexField):
    def __init__(self, **kwargs):
        super().__init__(
            USERNAME_PATTERN,
            min_length=3,
            max_length=20,
            error_messages={
                "invalid": "Nur Buchstaben, Ziffern und Unterstrich sind erlaubt.",
            },
            **kwargs,
        )


class ProfileSerializer(serializers.ModelSerializer):
    username = UsernameField()

    class Meta:
        model = Profile
        fields = ("username", "created_at")
        read_only_fields = ("created_at",)


class UsernameQuerySerializer(serializers.Serializer):
    username = UsernameField()


# Nibble is for people aged 16 and up (privacy policy, section 20)
MIN_AGE = 16


def age_on(birth_date, day):
    had_birthday = (day.month, day.day) >= (birth_date.month, birth_date.day)

    return day.year - birth_date.year - (0 if had_birthday else 1)


class BodyProfileSerializer(serializers.ModelSerializer):
    """Same limits as the calorie calculator, otherwise it couldn't use the values."""

    birth_date = serializers.DateField(allow_null=True, required=False)
    height_cm = serializers.IntegerField(
        min_value=120,
        max_value=250,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = BodyProfile
        fields = ("birth_date", "height_cm", "sex")
        extra_kwargs = {"sex": {"allow_null": True, "required": False}}

    def validate_birth_date(self, value):
        if value is None:
            return value

        age = age_on(value, timezone.localdate())

        if age < 0:
            raise serializers.ValidationError("Das Datum liegt in der Zukunft.")

        if age < MIN_AGE:
            raise serializers.ValidationError(
                f"Du musst mindestens {MIN_AGE} Jahre alt sein."
            )

        if age > 120:
            raise serializers.ValidationError("Prüf das Datum noch mal.")

        return value


EMPTY_BODY_PROFILE = {"birth_date": None, "height_cm": None, "sex": None}
