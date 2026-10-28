from django.contrib import admin

from .models import FoodProduct


@admin.register(FoodProduct)
class FoodProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "code", "base_unit", "kcal_per_100")
    search_fields = ("=code", "name", "brand")
    list_filter = ("base_unit",)
