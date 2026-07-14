from django.contrib import admin
from catalog.models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # Поля, которые будут отображаться в таблице
    list_display = ("id", "name", "slug")

    # Поля, по которым работает поиск
    search_fields = ("name",)

    # Поля, на которые можно нажать для перехода к редактированию
    list_display_links = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Поля, которые будут отображаться в таблице
    list_display = (
        "id",
        "name",
        "sku",
        "slug",
        "category",
        "price",
        "created_at",
        "updated_at",
        "published",
        "owner",
    )

    # Добавляем фильтр справа
    list_filter = ("category",)

    # Поля, по которым работает поиск
    search_fields = ("name",)

    # Поля, на которые можно нажать для перехода к редактированию
    list_display_links = ["name", "sku"]

    # Регистрируем наши кастомные массовые действия
    actions = ["make_published", "make_unpublished"]

    @admin.action(description="Опубликовать выбранные товары")
    def make_published(self, request, queryset):
        """Массово проставляет статус True (Опубликовано)."""
        updated = queryset.update(published=True)
        # Показываем красивое зеленое уведомление вверху админки
        self.message_user(
            request, f"Статус успешно изменен. Опубликовано товаров: {updated} шт."
        )

    @admin.action(description="Снять с публикации выбранные товары")
    def make_unpublished(self, request, queryset):
        """Массово проставляет статус False (Черновик)."""
        updated = queryset.update(published=False)
        # Показываем уведомление
        self.message_user(
            request,
            f"Статус успешно изменен. Снято с публикации товаров: {updated} шт.",
        )


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
