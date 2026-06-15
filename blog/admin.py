from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Настройка колонок в списке статей
    list_display = ("id", "title", "is_published", "views_count", "created_at")

    # Кликабельные колонки
    list_display_links = ("id", "title")

    # Поля, по которым можно искать статьи (например, по названию или тексту)
    search_fields = ("title", "content")

    # Фильтрация в правой панели админки
    list_filter = ("is_published", "created_at")

    # Позволяет быстро менять статус публикации прямо из списка
    list_editable = ("is_published",)
