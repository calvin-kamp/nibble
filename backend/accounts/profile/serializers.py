from rest_framework import serializers

from accounts.models import Profile

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
