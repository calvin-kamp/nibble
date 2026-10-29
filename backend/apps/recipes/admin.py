from django.contrib import admin

from .models import Recipe, RecipeIngredient, RecipeStep, RecipeSubmission


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


class RecipeStepInline(admin.TabularInline):
    model = RecipeStep
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "status", "kcal", "created_at")
    list_filter = ("status", "diet")
    search_fields = ("name",)
    readonly_fields = ("properties", "created_at", "updated_at")
    inlines = (RecipeIngredientInline, RecipeStepInline)


@admin.register(RecipeSubmission)
class RecipeSubmissionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "kind", "status", "submitted_at", "reviewed_by")
    list_filter = ("kind", "status")
    readonly_fields = ("submitted_at", "reviewed_at")
