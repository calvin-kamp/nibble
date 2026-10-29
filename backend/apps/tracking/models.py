from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


def macro_field(**kwargs):
    return models.DecimalField(
        max_digits=7,
        decimal_places=1,
        **kwargs,
    )


class Goal(models.TextChoices):
    LOSE = "lose", "Abnehmen"
    MAINTAIN = "maintain", "Gewicht halten"
    GAIN = "gain", "Zunehmen"


class MealType(models.TextChoices):
    BREAKFAST = "breakfast", "Frühstück"
    LUNCH = "lunch", "Mittagessen"
    DINNER = "dinner", "Abendessen"
    SNACK = "snack", "Snack"


class FoodUnit(models.TextChoices):
    G = "g", "g"
    ML = "ml", "ml"
    PORTION = "portion", "Portion"


class GoalSetting(models.Model):
    """Goal and targets valid from a day on; one row per day keeps the history."""

    profile = models.ForeignKey(
        "accounts.Profile",
        related_name="goal_settings",
        on_delete=models.CASCADE,
    )
    valid_from = models.DateField()

    goal = models.CharField(
        choices=Goal,
        max_length=8,
        blank=True,
        null=True,
    )

    # All four or none, see GoalUpdateSerializer.
    kcal = macro_field(blank=True, null=True)
    protein = macro_field(blank=True, null=True)
    carbs = macro_field(blank=True, null=True)
    fat = macro_field(blank=True, null=True)

    class Meta:
        ordering = ["-valid_from"]
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "valid_from"],
                name="unique_goal_setting_per_day",
            ),
        ]

    def __str__(self):
        return f"{self.profile} ab {self.valid_from}"

    @classmethod
    def valid_on(cls, profile, day):
        return (
            cls.objects.filter(profile=profile, valid_from__lte=day)
            .order_by("-valid_from")
            .first()
        )

    @property
    def has_targets(self):
        return self.kcal is not None


class FoodSnapshot(models.Model):
    """Product data copied at tracking time, so later OFF updates change nothing.

    kcal and macros are the values for amount and unit, rounded to one place.
    """

    off_code = models.CharField(
        max_length=14,
        blank=True,
        null=True,
    )
    food_name = models.CharField(max_length=255)
    brand = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    base_unit = models.CharField(
        max_length=2,
        blank=True,
        null=True,
    )

    kcal_per_100 = macro_field(blank=True, null=True)
    protein_per_100 = macro_field(blank=True, null=True)
    carbs_per_100 = macro_field(blank=True, null=True)
    fat_per_100 = macro_field(blank=True, null=True)
    serving_quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
    )

    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )
    unit = models.CharField(
        choices=FoodUnit,
        max_length=7,
    )

    kcal = macro_field()
    protein = macro_field()
    carbs = macro_field()
    fat = macro_field()

    class Meta:
        abstract = True


class TrackingEntry(FoodSnapshot):
    class Source(models.TextChoices):
        OFF = "off", "Open Food Facts"
        MEAL = "meal", "Eigene Mahlzeit"

    profile = models.ForeignKey(
        "accounts.Profile",
        related_name="tracking_entries",
        on_delete=models.CASCADE,
    )
    source = models.CharField(
        choices=Source,
        default=Source.OFF,
        max_length=4,
    )

    consumed_on = models.DateField()
    meal_type = models.CharField(
        choices=MealType,
        max_length=9,
    )
    tracked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["consumed_on", "tracked_at", "id"]
        indexes = [
            models.Index(fields=["profile", "consumed_on"]),
        ]

    def __str__(self):
        return f"{self.food_name} ({self.consumed_on})"


class Meal(models.Model):
    """The user's own combination of foods, not to be confused with MealType."""

    profile = models.ForeignKey(
        "accounts.Profile",
        related_name="meals",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=100)
    note = models.CharField(max_length=300, blank=True, default="")

    kcal = macro_field()
    protein = macro_field()
    carbs = macro_field()
    fat = macro_field()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class MealItem(FoodSnapshot):
    meal = models.ForeignKey(
        Meal,
        related_name="items",
        on_delete=models.CASCADE,
    )
    position = models.PositiveIntegerField()

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.food_name


class WeightEntry(models.Model):
    profile = models.ForeignKey(
        "accounts.Profile",
        related_name="weight_entries",
        on_delete=models.CASCADE,
    )
    weight_kg = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(20), MaxValueValidator(500)],
    )
    measured_on = models.DateField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["measured_on"]
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "measured_on"],
                name="unique_weight_entry_per_day",
            ),
        ]

    def __str__(self):
        return f"{self.weight_kg} kg ({self.measured_on})"
