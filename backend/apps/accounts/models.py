from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models.functions import Lower
from django.utils import timezone


class UserManager(BaseUserManager):
    @classmethod
    def normalize_email(cls, email):
        """Lowercases the whole address, so logins don't depend on spelling."""
        return (email or "").strip().lower()

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email must be set")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)

        # Every user needs a profile, also the ones from createsuperuser.
        with transaction.atomic(using=self._db):
            user.save(using=self._db)
            Profile.objects.create(user=user)

        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Authentication only; everything else hangs on the profile."""

    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    date_joined = models.DateTimeField(default=timezone.now)

    deletion_scheduled_for = models.DateTimeField(
        blank=True,
        null=True,
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email


class Profile(models.Model):
    class OnboardingStep(models.TextChoices):
        USERNAME = "username", "Username"
        CONSENT = "consent", "Einwilligung"
        GOAL = "goal", "Ziel"
        TARGETS = "targets", "Zielwerte"
        SUMMARY = "summary", "Zusammenfassung"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    username = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    onboarding_step = models.CharField(
        choices=OnboardingStep,
        default=OnboardingStep.USERNAME,
        max_length=8,
    )
    onboarding_completed = models.BooleanField(default=False)

    # None = no decision yet, False = declined or revoked.
    consent_accepted = models.BooleanField(
        blank=True,
        null=True,
    )
    consent_decided_at = models.DateTimeField(
        blank=True,
        null=True,
    )
    consent_policy_version = models.CharField(
        max_length=32,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("username"),
                name="unique_username_ignoring_case",
            ),
        ]

    def __str__(self):
        if self.username:
            return self.username

        return str(self.user)

    @property
    def has_consent(self):
        return self.consent_accepted is True


class ConsentRecord(models.Model):
    """One entry per consent decision; only ever added to, never changed.

    The profile keeps the current state; this history proves when and to which
    policy version the user consented or revoked. It goes with the account.
    """

    profile = models.ForeignKey(
        Profile,
        related_name="consent_records",
        on_delete=models.CASCADE,
    )
    accepted = models.BooleanField()
    policy_version = models.CharField(max_length=32)
    decided_at = models.DateTimeField()

    class Meta:
        ordering = ["decided_at", "id"]

    def __str__(self):
        decision = "Einwilligung" if self.accepted else "Widerruf"

        return f"{decision} ({self.policy_version}, {self.decided_at:%Y-%m-%d})"


class Sex(models.TextChoices):
    MALE = "male", "Männlich"
    FEMALE = "female", "Weiblich"


class BodyProfile(models.Model):
    """Date of birth, height and sex for the calorie calculator.

    Health data like tracking: only with consent, deleted on revoke.
    """

    profile = models.OneToOneField(
        Profile,
        related_name="body",
        on_delete=models.CASCADE,
    )
    birth_date = models.DateField(blank=True, null=True)
    height_cm = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(120), MaxValueValidator(250)],
    )
    sex = models.CharField(
        choices=Sex,
        max_length=6,
        blank=True,
        null=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Körperdaten von {self.profile}"
