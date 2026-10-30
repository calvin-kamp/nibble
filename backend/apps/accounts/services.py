from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.accounts.account.serializers import SubmissionExportSerializer
from apps.accounts.models import BodyProfile, Profile
from apps.accounts.onboarding.serializers import OnboardingStateSerializer
from apps.accounts.privacy.serializers import (
    ConsentRecordSerializer,
    ConsentStateSerializer,
)
from apps.accounts.profile.serializers import BodyProfileSerializer, ProfileSerializer
from apps.recipes.catalog.serializers import RecipeDetailSerializer
from apps.recipes.models import Recipe, RecipeSubmission
from apps.recipes.services import delete_recipe, delete_submission
from apps.tracking.nutrition.serializers import (
    GoalStateSerializer,
    MealSerializer,
    TrackingEntrySerializer,
)
from apps.tracking.weight.serializers import WeightEntrySerializer
from config.emails import send_template_email

from .tokens import (
    make_email_change_token,
    make_password_reset_token,
    make_verification_token,
)

# Onboarding rules: username -> consent -> goal -> targets -> summary.
#
# Saving a step's data moves the user on by itself (see advance()). PATCH
# /onboarding only covers jumps the backend can't see, e.g. "later" on the targets.

Step = Profile.OnboardingStep


def is_allowed(profile, step):
    if profile.onboarding_completed:
        return False

    if step == Step.USERNAME:
        return True

    if not profile.username:
        return False

    if step in (Step.GOAL, Step.TARGETS):
        return profile.consent_accepted is True

    if step == Step.SUMMARY:
        return profile.consent_accepted is not None

    return True


def go_to(profile, step):
    profile.onboarding_step = step
    profile.save(update_fields=["onboarding_step"])


def advance(profile, done_step, next_step):
    """Moves on after a step was saved, but only while the user is on that step."""
    if not profile.onboarding_completed and profile.onboarding_step == done_step:
        go_to(profile, next_step)


def after_consent_decision(profile):
    if profile.consent_accepted:
        advance(profile, Step.CONSENT, Step.GOAL)
        return

    # Declining skips goal and targets; revoking mid-way leaves them, too.
    if not profile.onboarding_completed and profile.onboarding_step in (
        Step.CONSENT,
        Step.GOAL,
        Step.TARGETS,
    ):
        go_to(profile, Step.SUMMARY)


def send_verification_email(user):
    link = f"{settings.FRONTEND_URL}/verify-email?token={make_verification_token(user)}"

    send_template_email(
        user.email,
        "Bitte bestätige deine E-Mail-Adresse",
        "verify_email",
        {"link": link},
    )


def send_email_change_email(user, new_email):
    """The link goes to the new address; only the click there makes it the account's."""
    token = make_email_change_token(user, new_email)
    link = f"{settings.FRONTEND_URL}/email-aendern?token={token}"

    send_template_email(
        new_email,
        "Bitte bestätige deine neue E-Mail-Adresse",
        "email_change",
        {"link": link},
    )


def send_email_change_requested_email(user, new_email):
    """Notice to the current address, in case the request did not come from the user.
    Notification only, so unverified accounts get nothing."""
    if not user.email_verified:
        return

    send_template_email(
        user.email,
        "Deine E-Mail-Adresse soll geändert werden",
        "email_change_requested",
        {"new_email": new_email},
    )


def send_password_reset_email(user):
    link = f"{settings.FRONTEND_URL}/reset-password?token={make_password_reset_token(user)}"

    send_template_email(
        user.email,
        "Passwort zurücksetzen",
        "password_reset",
        {"link": link},
    )


def send_password_changed_email(user):
    """Notification only, so unverified accounts get nothing."""
    if not user.email_verified:
        return

    send_template_email(
        user.email,
        "Dein Passwort wurde geändert",
        "password_changed",
        {},
    )


def send_deletion_scheduled_email(user):
    """Notification only, so unverified accounts get nothing."""
    if not user.email_verified:
        return

    deletion_date = timezone.localtime(user.deletion_scheduled_for)

    send_template_email(
        user.email,
        "Dein Konto wird gelöscht",
        "deletion_scheduled",
        {"deletion_date": f"{deletion_date:%d.%m.%Y um %H:%M}"},
    )


def send_account_deleted_email(user):
    """Notification only, so unverified accounts get nothing."""
    if not user.email_verified:
        return

    send_template_email(
        user.email,
        "Dein Konto wurde gelöscht",
        "account_deleted",
        {},
    )


@transaction.atomic
def delete_account(user):
    """Deletes the user and everything attached; approved recipes stay without author.

    Profile, consent, goals, tracking data, meals and saved recipes go with the
    profile via CASCADE. Recipes only get their author set to NULL, so the ones
    that were never approved and all unapproved revisions are removed here.
    """
    profile = user.profile

    for recipe in Recipe.objects.filter(author=profile).exclude(
        status=Recipe.Status.APPROVED
    ):
        delete_recipe(recipe)

    for submission in RecipeSubmission.objects.filter(
        recipe__author=profile,
        kind=RecipeSubmission.Kind.REVISION,
    ).exclude(status=Recipe.Status.APPROVED):
        delete_submission(submission)

    send_account_deleted_email(user)
    user.delete()


def build_export(request):
    """Everything stored about the user, see the ExportDocument schema."""
    user = request.user
    profile = user.profile

    document = {
        "exported_at": timezone.now(),
        "account": {
            "email": user.email,
            "email_verified": user.email_verified,
            "created_at": user.date_joined,
            "last_login": user.last_login,
            "deletion_scheduled_for": user.deletion_scheduled_for,
        },
        "profile": ProfileSerializer(profile).data,
        "onboarding": OnboardingStateSerializer(profile).data,
        "privacy_consent": ConsentStateSerializer(profile).data,
        "consent_history": ConsentRecordSerializer(
            profile.consent_records.all(), many=True
        ).data,
    }

    # Health data only exists with consent; revoking deletes it.
    if profile.has_consent:
        body = BodyProfile.objects.filter(profile=profile).first()

        document["body"] = BodyProfileSerializer(body).data if body else None
        document["goal_history"] = GoalStateSerializer(
            profile.goal_settings.order_by("valid_from"), many=True
        ).data
        document["weights"] = WeightEntrySerializer(
            profile.weight_entries.order_by("measured_on"), many=True
        ).data
        document["entries"] = TrackingEntrySerializer(
            profile.tracking_entries.order_by("consumed_on", "tracked_at"), many=True
        ).data
        document["meals"] = MealSerializer(
            profile.meals.prefetch_related("items").order_by("name"), many=True
        ).data

    document["recipes"] = RecipeDetailSerializer(
        Recipe.objects.filter(author=profile).prefetch_related("ingredients", "steps"),
        many=True,
        context={"request": request},
    ).data
    document["submissions"] = SubmissionExportSerializer(
        RecipeSubmission.objects.filter(recipe__author=profile).order_by(
            "submitted_at", "id"
        ),
        many=True,
        context={"request": request},
    ).data
    document["saved_recipe_ids"] = list(
        profile.saved_recipes.order_by("created_at").values_list("recipe_id", flat=True)
    )

    return document
