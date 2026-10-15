from django.contrib import admin

from .models import (
    BodyData,
    DailyGoal,
    DiaryEntry,
    DiaryEntryItem,
    Meal,
    MealItem,
    WeightEntry,
)


class MealItemInline(admin.TabularInline):
    model = MealItem
    autocomplete_fields = ("food",)
    extra = 0


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at")
    search_fields = ("name", "owner__email")
    raw_id_fields = ("owner",)
    inlines = (MealItemInline,)


class DiaryEntryItemInline(admin.TabularInline):
    model = DiaryEntryItem
    fields = ("name", "brand", "amount", "basis", "kcal_per_100")
    readonly_fields = fields
    extra = 0


@admin.register(DiaryEntry)
class DiaryEntryAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "section", "date", "owner", "deleted_at")
    list_filter = ("kind", "section", "date")
    search_fields = ("name", "owner__email")
    raw_id_fields = ("owner", "food", "meal")
    inlines = (DiaryEntryItemInline,)


@admin.register(WeightEntry)
class WeightEntryAdmin(admin.ModelAdmin):
    list_display = ("date", "weight", "owner")
    list_filter = ("date",)
    search_fields = ("owner__email",)
    raw_id_fields = ("owner",)


@admin.register(DailyGoal)
class DailyGoalAdmin(admin.ModelAdmin):
    list_display = ("owner", "valid_from", "source", "kcal")
    list_filter = ("source",)
    search_fields = ("owner__email",)
    raw_id_fields = ("owner",)


@admin.register(BodyData)
class BodyDataAdmin(admin.ModelAdmin):
    list_display = ("owner", "updated_at")
    search_fields = ("owner__email",)
    raw_id_fields = ("owner",)
