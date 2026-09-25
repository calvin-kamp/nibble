from decimal import Decimal

from django.db import transaction
from django.utils.encoding import smart_str
from rest_framework import serializers

from recipes.models import (
    Attribute,
    CookingStep,
    Diet,
    Equipment,
    Ingredient,
    Intolerance,
    MealType,
    Recipe,
    RecipeIngredient,
)

IMAGE_MAX_BYTES = 5 * 1024 * 1024
IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}

TAXONOMY_FIELDS = ("diets", "intolerances", "meal_types", "equipment", "attributes")


class ChoiceSlugRelatedField(serializers.SlugRelatedField):
    """Reads and writes taxonomy entries by their label, e.g. "Unter 30 Min"."""

    def to_representation(self, obj):
        return getattr(obj, f"get_{self.slug_field}_display")()

    def to_internal_value(self, data):
        choices = self.get_queryset().model._meta.get_field(self.slug_field).choices
        value = next((value for value, label in choices if label == data), None)

        if value is None:
            self.fail(
                "does_not_exist", slug_name=self.slug_field, value=smart_str(data)
            )

        return super().to_internal_value(value)


class UnitField(serializers.ChoiceField):
    """Exposes the unit by its label ("g", "EL"), stores the integer choice."""

    def __init__(self, **kwargs):
        super().__init__(choices=RecipeIngredient.UnitChoice.labels, **kwargs)

    def to_representation(self, value):
        return RecipeIngredient.UnitChoice(value).label

    def to_internal_value(self, data):
        label = super().to_internal_value(data)

        return next(unit for unit in RecipeIngredient.UnitChoice if unit.label == label)


class CookingStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = CookingStep
        fields = ("step", "text")
        # The position in the list decides the number, see RecipeDetailSerializer.
        read_only_fields = ("step",)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="ingredient.name", max_length=60)
    amount = serializers.DecimalField(
        max_digits=5,
        decimal_places=1,
        min_value=Decimal("0.1"),
        coerce_to_string=False,
    )
    unit = UnitField()

    class Meta:
        model = RecipeIngredient
        fields = ("name", "amount", "unit")


class RecipeBaseSerializer(serializers.ModelSerializer):
    """Fields shared by list and detail."""

    slug = serializers.ReadOnlyField()
    image = serializers.ImageField(read_only=True)

    diets = ChoiceSlugRelatedField(
        slug_field="diet",
        queryset=Diet.objects.all(),
        many=True,
        required=False,
    )
    intolerances = ChoiceSlugRelatedField(
        slug_field="intolerance",
        queryset=Intolerance.objects.all(),
        many=True,
        required=False,
    )
    meal_types = ChoiceSlugRelatedField(
        slug_field="meal_type",
        queryset=MealType.objects.all(),
        many=True,
        required=False,
    )
    equipment = ChoiceSlugRelatedField(
        slug_field="equipment",
        queryset=Equipment.objects.all(),
        many=True,
        required=False,
    )
    attributes = ChoiceSlugRelatedField(
        slug_field="attribute",
        queryset=Attribute.objects.all(),
        many=True,
        required=False,
    )


class RecipeListSerializer(RecipeBaseSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "slug",
            "image",
            "name",
            "duration_minutes",
            "diets",
            "intolerances",
            "meal_types",
            "equipment",
            "attributes",
            "kcal_per_serving",
            "created_at",
        )


class RecipeDetailSerializer(RecipeBaseSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    cooking_steps = CookingStepSerializer(many=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "slug",
            "image",
            "name",
            "description",
            "ingredients",
            "cooking_steps",
            "protein_per_serving",
            "carbs_per_serving",
            "fat_per_serving",
            "kcal_per_serving",
            "servings",
            "duration_minutes",
            "diets",
            "intolerances",
            "meal_types",
            "equipment",
            "attributes",
            "is_owner",
            "updated_at",
            "created_at",
        )
        extra_kwargs = {
            "protein_per_serving": {"coerce_to_string": False},
            "carbs_per_serving": {"coerce_to_string": False},
            "fat_per_serving": {"coerce_to_string": False},
        }

    def get_is_owner(self, obj):
        request = self.context.get("request")

        return bool(request and obj.owner_id and obj.owner_id == request.user.id)

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError("Füge mindestens eine Zutat hinzu.")

        return value

    def validate_cooking_steps(self, value):
        if not value:
            raise serializers.ValidationError("Beschreibe mindestens einen Schritt.")

        return value

    @transaction.atomic
    def create(self, validated_data):
        relations = self._pop_relations(validated_data)
        recipe = Recipe.objects.create(**validated_data)
        self._save_relations(recipe, relations)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        relations = self._pop_relations(validated_data)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()
        self._save_relations(instance, relations)

        return instance

    def _pop_relations(self, validated_data):
        """Nested lists and many-to-many fields can't go into Recipe(**data)."""
        names = (*TAXONOMY_FIELDS, "ingredients", "cooking_steps")

        return {
            name: validated_data.pop(name) for name in names if name in validated_data
        }

    def _save_relations(self, recipe, relations):
        """Replaces every relation that was sent; missing ones stay untouched (PATCH)."""
        if "ingredients" in relations:
            recipe.ingredients.all().delete()
            RecipeIngredient.objects.bulk_create(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=self._get_or_create_ingredient(
                        item["ingredient"]["name"]
                    ),
                    amount=item["amount"],
                    unit=item["unit"],
                )
                for item in relations["ingredients"]
            )

        if "cooking_steps" in relations:
            recipe.cooking_steps.all().delete()
            CookingStep.objects.bulk_create(
                CookingStep(recipe=recipe, step=number, text=item["text"])
                for number, item in enumerate(relations["cooking_steps"], start=1)
            )

        for name in TAXONOMY_FIELDS:
            if name in relations:
                getattr(recipe, name).set(relations[name])

    def _get_or_create_ingredient(self, name):
        """Case-insensitive, so "zwiebel" and "Zwiebel" share one entry."""
        ingredient = Ingredient.objects.filter(name__iexact=name).first()

        return ingredient or Ingredient.objects.create(name=name)


class RecipeImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = ("image",)

    def validate_image(self, image):
        # Pillow has already opened the file here, its format beats the file extension.
        if (
            getattr(image, "image", None) is None
            or image.image.format not in IMAGE_FORMATS
        ):
            raise serializers.ValidationError(
                "Dieses Format wird nicht unterstützt. Verwende JPG, PNG oder WebP."
            )

        if image.size > IMAGE_MAX_BYTES:
            raise serializers.ValidationError(
                "Das Bild ist größer als 5 MB. Wähle eine kleinere Datei."
            )

        return image
