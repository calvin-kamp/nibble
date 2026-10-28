from pathlib import Path

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify


def slug_for(name):
    """URL-safe name, umlauts spelled out like the frontend does."""
    for umlaut, replacement in (
        ("ä", "ae"),
        ("Ä", "Ae"),
        ("ö", "oe"),
        ("Ö", "Oe"),
        ("ü", "ue"),
        ("Ü", "Ue"),
        ("ß", "ss"),
    ):
        name = name.replace(umlaut, replacement)

    return slugify(name)


def recipe_image_path(instance, filename):
    """recipes/{id}-{slug}.{ext}; the file name never comes from the user."""
    return f"recipes/{instance.pk}-{slug_for(instance.name)}{Path(filename).suffix}"


def submission_image_path(instance, filename):
    recipe = instance.recipe

    return (
        f"recipes/revisions/{recipe.pk}-{slug_for(recipe.name)}{Path(filename).suffix}"
    )


def macro_field(**kwargs):
    return models.DecimalField(
        max_digits=7,
        decimal_places=1,
        validators=[MinValueValidator(0)],
        **kwargs,
    )


class RecipeQuerySet(models.QuerySet):
    def visible_to(self, user):
        """Approved recipes for everyone, unapproved ones only for author and staff."""
        if user.is_authenticated and user.is_staff:
            return self

        if user.is_authenticated:
            return self.filter(Q(status=Recipe.Status.APPROVED) | Q(author=user.profile))

        return self.filter(status=Recipe.Status.APPROVED)


class Recipe(models.Model):
    """The live version; changes to approved recipes wait in RecipeSubmission."""

    class Status(models.TextChoices):
        PENDING = "pending", "Offen"
        APPROVED = "approved", "Freigegeben"
        REJECTED = "rejected", "Abgelehnt"

    class Diet(models.TextChoices):
        VEGETARIAN = "vegetarian", "Vegetarisch"
        VEGAN = "vegan", "Vegan"
        PESCETARIAN = "pescetarian", "Pescetarisch"

    class Intolerance(models.TextChoices):
        GLUTEN_FREE = "gluten_free", "Glutenfrei"
        LACTOSE_FREE = "lactose_free", "Laktosefrei"

    class MealType(models.TextChoices):
        BREAKFAST = "breakfast", "Frühstück"
        LUNCH = "lunch", "Mittagessen"
        DINNER = "dinner", "Abendessen"
        SNACK = "snack", "Snack"
        DESSERT = "dessert", "Dessert"

    class Equipment(models.TextChoices):
        OVEN = "oven", "Backofen"
        STOVE = "stove", "Herd"
        MIXER = "mixer", "Mixer"
        AIRFRYER = "airfryer", "Airfryer"

    class Property(models.TextChoices):
        PROTEIN_RICH = "protein_rich", "Proteinreich"
        LOW_CALORIE = "low_calorie", "Kalorienarm"
        FEW_INGREDIENTS = "few_ingredients", "Wenig Zutaten"
        UNDER_30_MIN = "under_30_min", "Unter 30 Min"

    author = models.ForeignKey(
        "accounts.Profile",
        related_name="recipes",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    status = models.CharField(
        choices=Status,
        default=Status.PENDING,
        max_length=8,
    )
    rejection_reason = models.TextField(
        blank=True,
        null=True,
    )

    image = models.ImageField(
        upload_to=recipe_image_path,
        blank=True,
    )

    name = models.CharField(max_length=120)
    description = models.TextField(max_length=2000)
    prep_time_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10080)],
    )
    servings = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )

    diet = models.CharField(
        choices=Diet,
        max_length=11,
        blank=True,
        null=True,
    )
    intolerances = ArrayField(
        models.CharField(choices=Intolerance, max_length=12),
        default=list,
        blank=True,
    )
    equipment = ArrayField(
        models.CharField(choices=Equipment, max_length=8),
        default=list,
        blank=True,
    )
    meal_types = ArrayField(
        models.CharField(choices=MealType, max_length=9),
        default=list,
    )
    # Computed on save, see submissions.compute_properties().
    properties = ArrayField(
        models.CharField(choices=Property, max_length=15),
        default=list,
        blank=True,
    )

    kcal = macro_field()
    protein = macro_field()
    carbs = macro_field()
    fat = macro_field()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RecipeQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    class Unit(models.TextChoices):
        G = "g", "g"
        KG = "kg", "kg"
        ML = "ml", "ml"
        L = "l", "l"
        TBSP = "tbsp", "EL"
        TSP = "tsp", "TL"
        PIECE = "piece", "Stück"
        PINCH = "pinch", "Prise"
        CUP = "cup", "Tasse"
        SLICE = "slice", "Scheibe"
        BUNCH = "bunch", "Bund"
        CLOVE = "clove", "Zehe"
        CAN = "can", "Dose"
        PACK = "pack", "Packung"

    recipe = models.ForeignKey(
        Recipe,
        related_name="ingredients",
        on_delete=models.CASCADE,
    )
    position = models.PositiveIntegerField()

    name = models.CharField(max_length=100)
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )
    unit = models.CharField(
        choices=Unit,
        max_length=5,
    )

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.name


class RecipeStep(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name="steps",
        on_delete=models.CASCADE,
    )
    step_number = models.PositiveIntegerField()
    text = models.TextField(max_length=2000)

    class Meta:
        ordering = ["step_number"]

    def __str__(self):
        return f"{self.step_number}. {self.text}"


class RecipeSubmission(models.Model):
    """A new recipe or a change to an approved one, waiting for moderation.

    The content is stored as RecipeInput JSON. For new recipes it mirrors the
    recipe itself; revisions only reach the recipe on approval.
    """

    class Kind(models.TextChoices):
        NEW = "new", "Neues Rezept"
        REVISION = "revision", "Änderung"

    class ImageAction(models.TextChoices):
        KEEP = "keep", "Beibehalten"
        REPLACE = "replace", "Ersetzen"
        REMOVE = "remove", "Entfernen"

    recipe = models.ForeignKey(
        Recipe,
        related_name="submissions",
        on_delete=models.CASCADE,
    )
    kind = models.CharField(
        choices=Kind,
        max_length=8,
    )
    status = models.CharField(
        choices=Recipe.Status,
        default=Recipe.Status.PENDING,
        max_length=8,
    )

    content = models.JSONField()

    # Revisions only; new recipes carry their image themselves.
    image = models.ImageField(
        upload_to=submission_image_path,
        blank=True,
    )
    image_action = models.CharField(
        choices=ImageAction,
        default=ImageAction.KEEP,
        max_length=7,
    )

    submitted_at = models.DateTimeField(default=timezone.now)

    reviewed_by = models.ForeignKey(
        "accounts.Profile",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    reviewed_at = models.DateTimeField(
        blank=True,
        null=True,
    )
    rejection_reason = models.TextField(
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["submitted_at", "id"]

    def __str__(self):
        return f"{self.get_kind_display()}: {self.content.get('name', self.recipe)}"

    @property
    def effective_image(self):
        """The image the recipe will have once this submission is approved."""
        if self.kind == self.Kind.REVISION:
            if self.image_action == self.ImageAction.REPLACE:
                return self.image

            if self.image_action == self.ImageAction.REMOVE:
                return None

        return self.recipe.image or None


class SavedRecipe(models.Model):
    profile = models.ForeignKey(
        "accounts.Profile",
        related_name="saved_recipes",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="saved_by",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "recipe"],
                name="unique_saved_recipe",
            ),
        ]

    def __str__(self):
        return f"{self.profile} → {self.recipe}"
