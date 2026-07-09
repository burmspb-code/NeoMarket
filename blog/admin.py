from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Настройка колонок в списке статей
    list_display = ("id", "title", "is_published", "views_count", "created_at", "owner")

    # Кликабельные колонки
    list_display_links = ("id", "title")

    # Поля, по которым можно искать статьи (например, по названию или тексту)
    search_fields = ("title", "content", "owner__email")

    # Фильтрация в правой панели админки
    list_filter = ("is_published", "created_at", "owner")

    # Позволяет быстро менять статус публикации прямо из списка
    list_editable = ("is_published",)

    # Регистрируем наши кастомные массовые действия
    actions = ["make_published", "make_unpublished"]

    @admin.action(description="Опубликовать выбранные статьи")
    def make_published(self, request, queryset):
        """Массово проставляет статус True (Опубликовано)."""
        updated = queryset.update(is_published=True)
        # Показываем красивое зеленое уведомление вверху админки
        self.message_user(
            request, f"Статус успешно изменен. Опубликовано статей: {updated} шт."
        )

    @admin.action(description="Снять с публикации выбранные статьи")
    def make_unpublished(self, request, queryset):
        """Массово проставляет статус False (Черновик)."""
        updated = queryset.update(is_published=False)
        # Показываем уведомление
        self.message_user(
            request, f"Статус успешно изменен. Снято с публикации статей: {updated} шт."
        )
