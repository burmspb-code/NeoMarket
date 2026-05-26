from django.contrib import admin
from .models import Author, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    # Колонки в общем списке
    list_display = ("first_name", "last_name", "birth_date")

    # Выбираем фильтр
    list_filter = ("last_name",)

    # Выбираем поля для поиска
    search_fields = ("first_name", "last_name")


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # Колонки в общем списке
    list_display = ("title", "publication_date", "author")

    # Выбираем фильтр
    list_filter = ("author",)

    # Выбираем поля для поиска
    search_fields = ("title",)
