from django.contrib import admin
from catalog.models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
        "image",
        "category",
        "price",
        "created_at",
        "updated_at",
    )
    list_filter = ("category",)
    search_fields = ("name", "description")
