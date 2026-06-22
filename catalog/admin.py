from django.contrib import admin
from catalog.models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "sku",
        "description",
        "category",
        "price",
        "created_at",
        "updated_at",
    )
    list_filter = ("category",)
    search_fields = ("name", "description")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    # Добавляем get_sku в список отображаемых колонок таблицы
    list_display = ("id", "product", "get_sku", "image")
    list_filter = ("product",)

    # Кастомный метод, который вытаскивает артикул связанного товара
    @admin.display(ordering="product__sku", description="Артикул товара")
    def get_sku(self, obj):
        # Проверяем, привязан ли товар, чтобы не вызвать ошибку
        return obj.product.sku if obj.product else "Не указан"
