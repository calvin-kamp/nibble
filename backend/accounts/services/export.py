from django.utils import timezone

from accounts.account.serializers import SubmissionExportSerializer
from accounts.onboarding.serializers import OnboardingStateSerializer
from accounts.privacy.serializers import ConsentRecordSerializer, ConsentStateSerializer
from accounts.profile.serializers import ProfileSerializer
from recipes.api.serializers import RecipeDetailSerializer
from recipes.models import Recipe, RecipeSubmission
from tracking.api.serializers import (
    BodyProfileSerializer,
    GoalStateSerializer,
    MealSerializer,
    TrackingEntrySerializer,
    WeightEntrySerializer,
)
from tracking.models import BodyProfile


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
