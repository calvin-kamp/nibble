from decimal import Decimal

from rest_framework import serializers

from apps.recipes.models import Recipe, RecipeIngredient, RecipeSubmission, SavedRecipe
from apps.recipes.utils import without_metadata
from config.fields import RoundedDecimalField
from config.serializers import MacrosSerializer

IMAGE_MAX_BYTES = 5 * 1024 * 1024
IMAGE_EXTENSIONS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
# Many phones write MPO: a JPEG with further pictures (e.g. depth or a second lens) appended.
# The first picture is a plain JPEG, so it is stored as one.
SAVED_AS = {"MPO": "JPEG"}


def absolute_url(request, file):
    if not file:
        return None

    return request.build_absolute_uri(file.url) if request else file.url


def author_data(profile):
    """For moderation only; public recipe responses never name the author.

    None once the author has deleted the account.
    """
    if profile is None:
        return None

    return {"username": profile.username}


def can_see_drafts(user, recipe):
    return user.is_authenticated and (
        user.is_staff or recipe.author_id == user.profile.pk
    )


class UniqueChoiceListField(serializers.ListField):
    """List of enum values where every value may appear only once."""

    def __init__(self, choices, **kwargs):
        super().__init__(child=serializers.ChoiceField(choices=choices), **kwargs)

    def to_internal_value(self, data):
        values = super().to_internal_value(data)

        if len(set(values)) != len(values):
            raise serializers.ValidationError("Jeder Wert darf nur einmal vorkommen.")

        return values


class IngredientSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    amount = RoundedDecimalField(
        decimal_places=2,
        min_value=Decimal("0.01"),
        max_value=100000,
    )
    unit = serializers.ChoiceField(choices=RecipeIngredient.Unit)


class StepSerializer(serializers.Serializer):
    step_number = serializers.IntegerField(min_value=1)
    text = serializers.CharField(max_length=2000)


class RecipeInputSerializer(serializers.Serializer):
    """Recipe content as the author sends it (RecipeInput).

    Validated data is flat like the Recipe model (kcal, protein ... on top
    level), so it also renders a Recipe or a stored submission back to JSON.
    """

    name = serializers.CharField(min_length=3, max_length=120)
    description = serializers.CharField(max_length=2000)
    prep_time_minutes = serializers.IntegerField(min_value=1, max_value=10080)
    diet = serializers.ChoiceField(
        choices=Recipe.Diet,
        allow_null=True,
        required=False,
        default=None,
    )
    intolerances = UniqueChoiceListField(
        Recipe.Intolerance,
        required=False,
        default=list,
    )
    equipment = UniqueChoiceListField(
        Recipe.Equipment,
        required=False,
        default=list,
    )
    meal_types = UniqueChoiceListField(Recipe.MealType, min_length=1)
    servings = serializers.IntegerField(min_value=1, max_value=100)
    nutrition_per_serving = MacrosSerializer(source="*")
    ingredients = IngredientSerializer(many=True, min_length=1, max_length=100)
    steps = StepSerializer(many=True, min_length=1, max_length=100)

    def validate_steps(self, steps):
        numbers = [step["step_number"] for step in steps]

        if numbers != list(range(1, len(steps) + 1)):
            raise serializers.ValidationError(
                "Die Schritte müssen lückenlos bei 1 beginnen und in der "
                "Reihenfolge der Liste stehen."
            )

        return steps


class RecipeOutputMixin:
    """Fields shared by list and detail that depend on the request."""

    def get_image_url(self, recipe):
        return absolute_url(self.context.get("request"), recipe.image)

    def get_is_own(self, recipe):
        """Whether the signed-in user wrote the recipe; None without login."""
        request = self.context.get("request")

        if request is None or not request.user.is_authenticated:
            return None

        return recipe.author_id == request.user.profile.pk

    def get_is_saved(self, recipe):
        """Uses the annotation from the view, queries otherwise; None without login."""
        request = self.context.get("request")

        if request is None or not request.user.is_authenticated:
            return None

        if hasattr(recipe, "saved"):
            return recipe.saved

        return SavedRecipe.objects.filter(
            recipe=recipe, profile=request.user.profile
        ).exists()


class RecipeListSerializer(RecipeOutputMixin, serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    nutrition_per_serving = MacrosSerializer(source="*", read_only=True)
    is_own = serializers.SerializerMethodField()
    has_pending_revision = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image_url",
            "prep_time_minutes",
            "diet",
            "intolerances",
            "equipment",
            "meal_types",
            "properties",
            "nutrition_per_serving",
            "is_own",
            "status",
            "has_pending_revision",
            "is_saved",
        )

    def get_has_pending_revision(self, recipe):
        if hasattr(recipe, "revision_pending"):
            return recipe.revision_pending

        return recipe.submissions.filter(
            kind=RecipeSubmission.Kind.REVISION,
            status=Recipe.Status.PENDING,
        ).exists()


class PendingRevisionSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    content = serializers.JSONField()

    class Meta:
        model = RecipeSubmission
        fields = (
            "id",
            "status",
            "submitted_at",
            "rejection_reason",
            "image_url",
            "content",
        )

    def get_image_url(self, submission):
        return absolute_url(self.context.get("request"), submission.effective_image)


class RecipeDetailSerializer(RecipeOutputMixin, RecipeInputSerializer):
    id = serializers.IntegerField(read_only=True)
    image_url = serializers.SerializerMethodField()
    properties = serializers.ListField(child=serializers.CharField(), read_only=True)
    is_own = serializers.SerializerMethodField()
    status = serializers.CharField(read_only=True)
    rejection_reason = serializers.CharField(read_only=True)
    pending_revision = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def get_pending_revision(self, recipe):
        """Latest revision unless approved; only author and staff see it."""
        request = self.context.get("request")

        if request is None or not can_see_drafts(request.user, recipe):
            return None

        revision = (
            recipe.submissions.filter(kind=RecipeSubmission.Kind.REVISION)
            .order_by("-submitted_at", "-id")
            .first()
        )

        if revision is None or revision.status == Recipe.Status.APPROVED:
            return None

        return PendingRevisionSerializer(revision, context=self.context).data


class RecipeImageSerializer(serializers.Serializer):
    image = serializers.ImageField()

    def validate_image(self, image):
        # Pillow has already opened the file here, its format beats the file extension.
        image_format = getattr(getattr(image, "image", None), "format", None)
        image_format = SAVED_AS.get(image_format, image_format)

        if image_format not in IMAGE_EXTENSIONS:
            raise serializers.ValidationError(
                "Dieses Format wird nicht unterstützt. Verwende JPG, PNG oder WebP."
            )

        if image.size > IMAGE_MAX_BYTES:
            raise serializers.ValidationError(
                "Das Bild ist größer als 5 MB. Wähle eine kleinere Datei."
            )

        # Saved without EXIF, XMP and IPTC. The stored name comes from the recipe,
        # only the extension is kept.
        return without_metadata(
            image, image_format, f"image{IMAGE_EXTENSIONS[image_format]}"
        )
