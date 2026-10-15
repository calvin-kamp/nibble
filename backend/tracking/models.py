from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from food.models import NUTRIENTS, Food, NutrientsPer100

WEIGHT_MIN = 20
WEIGHT_MAX = 400
SERVINGS_MIN = Decimal("0.5")
SERVINGS_MAX = 20
SERVINGS_STEP = Decimal("0.5")
MEAL_ITEMS_MAX = 30
# In grams or millilitres.
AMOUNT_MAX = 10000


class Section(models.TextChoices):
    """Fixed sections of a day, in this order everywhere in the app."""

    BREAKFAST = "fruehstueck", "Frühstück"
    LUNCH = "mittagessen", "Mittagessen"
    DINNER = "abendessen", "Abendessen"
    SNACKS = "snacks", "Snacks"
    DESSERT = "dessert", "Dessert"


class Meal(models.Model):
    """A saved combination of foods, private to its owner. One serving = all of it."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="meals", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=80)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name


class MealItem(models.Model):
    meal = models.ForeignKey(Meal, related_name="items", on_delete=models.CASCADE)
    # A food used in a meal can't be deleted from the database by accident.
    food = models.ForeignKey(Food, on_delete=models.PROTECT)
    # In the food's basis unit (g or ml).
    amount = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.1")), MaxValueValidator(AMOUNT_MAX)],
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.amount} {self.food.basis} {self.food}"


class DiaryEntryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted_at__isnull=True)


class DiaryEntry(models.Model):
    """One line of a day: a single food or one of the user's meals.

    The values are frozen in DiaryEntryItem rows when the entry is created, so
    later changes to a food or a meal never rewrite past days. Removing an entry
    only marks it (deleted_at) to allow "Rückgängig"; purge_deleted_entries
    deletes it for good later.
    """

    class Kind(models.TextChoices):
        FOOD = "food", "Lebensmittel"
        MEAL = "meal", "Mahlzeit"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="diary_entries", on_delete=models.CASCADE
    )
    date = models.DateField()
    section = models.CharField(max_length=11, choices=Section)
    kind = models.CharField(max_length=4, choices=Kind)
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=120, blank=True)

    # Food entries: amount = quantity × unit_amount, unit copied from the food.
    food = models.ForeignKey(Food, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.DecimalField(
        max_digits=7, decimal_places=1, null=True, blank=True
    )
    unit_key = models.CharField(max_length=10, blank=True)
    unit_name = models.CharField(max_length=20, blank=True)
    unit_amount = models.DecimalField(
        max_digits=6, decimal_places=1, null=True, blank=True
    )

    # Meal entries: the items hold one serving.
    meal = models.ForeignKey(Meal, null=True, blank=True, on_delete=models.SET_NULL)
    servings = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True
    )

    deleted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = DiaryEntryQuerySet.as_manager()

    class Meta:
        ordering = ["created_at", "id"]
        verbose_name_plural = "diary entries"
        indexes = [models.Index(fields=["owner", "date"])]

    def __str__(self):
        return f"{self.date} {self.get_section_display()}: {self.name}"

    @property
    def factor(self):
        """Meal items hold one serving; food entries have exactly one item."""
        return self.servings if self.kind == self.Kind.MEAL else Decimal(1)

    def nutrients(self, items=None):
        """Unrounded totals; pass prefetched items to avoid a query."""
        items = self.items.all() if items is None else items
        totals = dict.fromkeys(NUTRIENTS, Decimal(0))

        for item in items:
            for name, value in item.nutrients_for(item.amount * self.factor).items():
                totals[name] += value

        return totals


class DiaryEntryItem(NutrientsPer100):
    """Frozen copy of a food in an entry: name, values and amount at logging time."""

    entry = models.ForeignKey(
        DiaryEntry, related_name="items", on_delete=models.CASCADE
    )
    food = models.ForeignKey(Food, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=120, blank=True)
    # Basis unit; for meal entries per serving.
    amount = models.DecimalField(max_digits=8, decimal_places=1)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.amount} {self.basis} {self.name}"

    @classmethod
    def copy_of(cls, food, amount):
        return cls(
            food=food,
            name=food.name,
            brand=food.brand,
            basis=food.basis,
            amount=amount,
            **{f"{name}_per_100": value for name, value in food.per_100.items()},
        )


class WeightEntry(models.Model):
    """Body weight on one day; saving a day again replaces the value."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="weight_entries",
        on_delete=models.CASCADE,
    )
    date = models.DateField()
    weight = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(WEIGHT_MIN), MaxValueValidator(WEIGHT_MAX)],
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date"]
        verbose_name_plural = "weight entries"
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "date"], name="weight_once_per_day"
            ),
        ]

    def __str__(self):
        return f"{self.date}: {self.weight} kg"


class Sex(models.TextChoices):
    FEMALE = "female", "Weiblich"
    MALE = "male", "Männlich"


class Goal(models.TextChoices):
    DIET = "diet", "Abnehmen"
    MAINTAIN = "maintain", "Gewicht halten"
    GAIN = "gain", "Zunehmen"


class BodyData(models.Model):
    """The inputs of the calorie calculator, the only place that edits them.

    Fields stay empty when the daily goal was entered directly (then only the
    height is known). The weight isn't kept here: the current weight is the last
    measurement, the weight of a calculation sits on its DailyGoal.
    """

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="body_data", on_delete=models.CASCADE
    )
    sex = models.CharField(max_length=6, choices=Sex, blank=True)
    # The calculator asks for the age; with the day it was given it stays right
    # as the years pass, see current_age.
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    age_given_on = models.DateField(null=True, blank=True)
    height = models.PositiveSmallIntegerField(null=True, blank=True)
    steps = models.PositiveIntegerField(null=True, blank=True)
    # [{"met": "1-2-4.5", "duration": 60, "frequency": 3}, …] as in the calculator.
    workouts = models.JSONField(default=list, blank=True)
    goal = models.CharField(max_length=8, choices=Goal, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "body data"

    def __str__(self):
        return f"Körperdaten von {self.owner}"

    def current_age(self, today):
        if self.age is None or self.age_given_on is None:
            return None

        given = self.age_given_on
        years = (
            today.year
            - given.year
            - ((today.month, today.day) < (given.month, given.day))
        )

        return self.age + max(years, 0)


class DailyGoal(models.Model):
    """A version of the daily goal, valid from a day until the next version.

    Past days keep the goal that applied to them. Saving again on the same day
    adds a version that wins over the earlier ones; they stay, so a calculated
    goal remains available after switching to a custom value.
    """

    class Source(models.TextChoices):
        CALCULATED = "berechnet", "Berechnet"
        CUSTOM = "eigener-wert", "Eigener Wert"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="daily_goals", on_delete=models.CASCADE
    )
    valid_from = models.DateField()
    source = models.CharField(max_length=12, choices=Source)
    kcal = models.PositiveSmallIntegerField()
    protein = models.PositiveSmallIntegerField()
    carbs = models.PositiveSmallIntegerField()
    fat = models.PositiveSmallIntegerField()
    # A custom goal's macros are either derived from kcal, height and weight
    # (False) or entered by the person (True).
    custom_macros = models.BooleanField(default=False)
    # Weight the goal was calculated with, for "Gewicht hat sich geändert".
    weight = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(WEIGHT_MIN), MaxValueValidator(WEIGHT_MAX)],
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-valid_from", "-id"]
        indexes = [models.Index(fields=["owner", "valid_from"])]

    def __str__(self):
        return f"{self.kcal} kcal ab {self.valid_from}"
