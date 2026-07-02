from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Настройка отображения кастомной модели пользователя в админке."""

    # Поля которые будут выводится в панели
    list_display = ('username', 'email', 'phone_number', 'avatar', 'is_staff', 'is_superuser', 'is_active')

    # Поля по которым можно делать фильтрацию
    list_filter = ('is_staff', 'is_superuser', 'is_active')
