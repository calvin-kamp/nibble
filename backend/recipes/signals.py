from django.dispatch import receiver

from accounts.signals import personal_data_export

from .models import Recipe


@receiver(personal_data_export)
def export_own_recipes(sender, user, **kwargs):
    recipes = Recipe.objects.filter(owner=user).prefetch_related(
        "ingredients__ingredient", "cooking_steps"
    )

    return {
        "recipes": [
            {
                "name": recipe.name,
                "description": recipe.description,
                "servings": recipe.servings,
                "duration_minutes": recipe.duration_minutes,
                "kcal_per_serving": recipe.kcal_per_serving,
                "created_at": recipe.created_at,
                "ingredients": [
                    {
                        "name": item.ingredient.name,
                        "amount": item.amount,
                        "unit": item.get_unit_display(),
                    }
                    for item in recipe.ingredients.all()
                ],
                "steps": [step.text for step in recipe.cooking_steps.all()],
            }
            for recipe in recipes
        ]
    }
