from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from food.api.serializers import FoodSerializer, NutrientsSerializer
from food.models import NUTRIENTS, Food
from tracking.models import AMOUNT_MAX, MEAL_ITEMS_MAX, Meal, MealItem

AMOUNT_MESSAGE = "Gib eine Menge größer als 0 ein."


class MealItemSerializer(serializers.ModelSerializer):
    """Written as {food: id, amount}, read with the whole food for the editor."""

    food = serializers.PrimaryKeyRelatedField(queryset=Food.objects.all())
    amount = serializers.DecimalField(
        max_digits=6,
        decimal_places=1,
        min_value=Decimal("0.1"),
        max_value=Decimal(AMOUNT_MAX),
        coerce_to_string=False,
        error_messages={"min_value": AMOUNT_MESSAGE, "invalid": AMOUNT_MESSAGE},
    )

    class Meta:
        model = MealItem
        fields = ("food", "amount")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["food"] = FoodSerializer(instance.food, context=self.context).data

        return data


class MealSerializer(serializers.ModelSerializer):
    """A meal with its foods; nutrients are calculated per serving, never typed."""

    name = serializers.CharField(
        max_length=80,
        error_messages={"blank": "Gib der Mahlzeit einen Namen."},
    )
    items = MealItemSerializer(many=True)
    nutrients = serializers.SerializerMethodField()

    class Meta:
        model = Meal
        fields = ("id", "name", "items", "nutrients")

    def get_nutrients(self, meal):
        totals = dict.fromkeys(NUTRIENTS, Decimal(0))

        for item in meal.items.all():
            for name, value in item.food.nutrients_for(item.amount).items():
                totals[name] += value

        return NutrientsSerializer(totals).data

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Füge mindestens ein Lebensmittel hinzu.")

        if len(items) > MEAL_ITEMS_MAX:
            raise serializers.ValidationError(
                f"Eine Mahlzeit hat höchstens {MEAL_ITEMS_MAX} Lebensmittel."
            )

        return items

    @transaction.atomic
    def create(self, validated_data):
        items = validated_data.pop("items")
        meal = Meal.objects.create(**validated_data)
        self._save_items(meal, items)

        return meal

    @transaction.atomic
    def update(self, meal, validated_data):
        items = validated_data.pop("items", None)
        meal.name = validated_data.get("name", meal.name)
        meal.save()

        if items is not None:
            meal.items.all().delete()
            self._save_items(meal, items)

        return meal

    def _save_items(self, meal, items):
        """The order of the list is the order in the meal."""
        MealItem.objects.bulk_create(
            MealItem(meal=meal, food=item["food"], amount=item["amount"])
            for item in items
        )
