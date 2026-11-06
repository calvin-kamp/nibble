from django.contrib import admin

from .models import FoodProduct, FoodReport, MissingBarcode


@admin.register(FoodProduct)
class FoodProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "code", "base_unit", "kcal_per_100", "generic", "curated_at")
    search_fields = ("=code", "name", "brand")
    list_filter = ("base_unit", "generic", ("curated_at", admin.EmptyFieldListFilter))


@admin.register(MissingBarcode)
class MissingBarcodeAdmin(admin.ModelAdmin):
    list_display = ("code", "lookups", "first_searched_at", "last_searched_at")
    search_fields = ("=code",)


@admin.register(FoodReport)
class FoodReportAdmin(admin.ModelAdmin):
    list_display = ("product", "reason", "created_at")
    list_filter = ("reason",)
    search_fields = ("=product__code", "product__name")
    raw_id_fields = ("product",)
