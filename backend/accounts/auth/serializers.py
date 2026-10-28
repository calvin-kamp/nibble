from django.contrib.auth.password_validation import (
    validate_password as django_validate_password,
)
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from accounts.models import User
from accounts.onboarding.serializers import OnboardingStateSerializer


def validate_new_password(password, user):
    try:
        django_validate_password(password, user=user)
    except DjangoValidationError as exc:
        raise serializers.ValidationError({"new_password": list(exc.messages)}) from exc


class PasswordField(serializers.CharField):
    def __init__(self, **kwargs):
        kwargs.setdefault("write_only", True)
        kwargs.setdefault("trim_whitespace", False)
        super().__init__(**kwargs)


class NewPasswordField(PasswordField):
    def __init__(self, **kwargs):
        super().__init__(min_length=8, max_length=128, **kwargs)


class AccountStateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="profile.username", allow_null=True)
    privacy_consent = serializers.BooleanField(
        source="profile.consent_accepted",
        allow_null=True,
    )
    onboarding = OnboardingStateSerializer(source="profile")

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "email_verified",
            "username",
            "privacy_consent",
            "onboarding",
            "is_staff",
            "deletion_scheduled_for",
        )


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = NewPasswordField()

    def validate_email(self, value):
        return User.objects.normalize_email(value)

    def validate(self, attrs):
        try:
            django_validate_password(attrs["password"], user=User(email=attrs["email"]))
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc

        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = PasswordField()

    def validate_email(self, value):
        return User.objects.normalize_email(value)


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class PasswordChangeSerializer(serializers.Serializer):
    current_password = PasswordField()
    new_password = NewPasswordField()

    def validate_current_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Das aktuelle Passwort ist falsch.")

        return value

    def validate(self, attrs):
        validate_new_password(attrs["new_password"], self.context["request"].user)

        return attrs


class EmailChangeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = PasswordField()

    def validate_email(self, value):
        email = User.objects.normalize_email(value)

        if email == self.context["request"].user.email:
            raise serializers.ValidationError("Das ist bereits deine E-Mail-Adresse.")

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "Diese E-Mail-Adresse gehört schon zu einem anderen Konto."
            )

        return email

    def validate_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Das Passwort ist falsch.")

        return value


class PasswordForgotSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return User.objects.normalize_email(value)


class PasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = NewPasswordField()
