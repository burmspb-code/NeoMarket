from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Настройка отображения кастомной модели пользователя в админке."""

    # Исправляем ошибку сортировки (указываем email вместо дефолтного username)
    ordering = ("email",)

    # Убрали 'username' из списка, так как этого поля больше нет в модели
    list_display = (
        "email",
        "phone_number",
        "avatar",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    # Поля, по которым можно делать фильтрацию в правой колонке админки
    list_filter = ("is_staff", "is_superuser", "is_active")

    # Настройки полей при редактировании (убираем username из стандартных форм Django)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Личная информация",
            {"fields": ("first_name", "last_name", "phone_number", "avatar")},
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
