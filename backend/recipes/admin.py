from django.contrib import admin

from .models import CookingStep, Ingredient, Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    autocomplete_fields = ("ingredient",)
    extra = 0


class CookingStepInline(admin.TabularInline):
    model = CookingStep
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "kcal_per_serving", "created_at")
    list_filter = ("meal_types", "diets")
    search_fields = ("name",)
    readonly_fields = ("kcal_per_serving", "created_at", "updated_at")
    filter_horizontal = (
        "diets",
        "intolerances",
        "meal_types",
        "equipment",
        "attributes",
    )
    inlines = (RecipeIngredientInline, CookingStepInline)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ("name",)
