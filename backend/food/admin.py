from django.contrib import admin

from .models import Food, FoodUnit


class FoodUnitInline(admin.TabularInline):
    model = FoodUnit
    extra = 0


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "basis", "kcal_per_100", "barcode", "source")
    list_filter = ("source", "basis")
    search_fields = ("name", "brand", "barcode")
    readonly_fields = ("created_at", "updated_at")
    inlines = (FoodUnitInline,)
