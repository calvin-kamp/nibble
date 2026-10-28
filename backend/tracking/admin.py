from django.contrib import admin

from .models import GoalSetting, Meal, MealItem, TrackingEntry, WeightEntry


class MealItemInline(admin.TabularInline):
    model = MealItem
    extra = 0


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ("name", "profile", "kcal")
    inlines = (MealItemInline,)


@admin.register(TrackingEntry)
class TrackingEntryAdmin(admin.ModelAdmin):
    list_display = ("food_name", "profile", "consumed_on", "meal_type", "kcal")
    list_filter = ("source", "meal_type")


@admin.register(GoalSetting)
class GoalSettingAdmin(admin.ModelAdmin):
    list_display = ("profile", "valid_from", "goal", "kcal")


@admin.register(WeightEntry)
class WeightEntryAdmin(admin.ModelAdmin):
    list_display = ("profile", "measured_on", "weight_kg")
