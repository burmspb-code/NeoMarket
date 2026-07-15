"""Настройки административной панели для управления пользователями и их маркетинговыми статусами."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Настройка отображения кастомной модели пользователя в админке."""

    # Сортировка по email
    ordering = ("email",)

    # Убрали 'username' из списка, добавили красивые кастомные отображения статусов
    list_display = (
        "email",
        "phone_number",
        "avatar",
        "is_staff",
        "is_superuser",
        "is_active",
        "get_groups",
        "is_subscribed_status",  # Изменено: красивый статус подписки
        "email_status_badge",    # Изменено: цветной бейдж статуса почты
        "subscription_updated_at",
    )

    # Расширили фильтры, чтобы маркетологи могли быстро сегментировать базу
    list_filter = ("is_subscribed", "email_status", "is_staff", "is_superuser", "is_active")

    # Важно: поля с автоматической датой должны быть доступны только для чтения!
    readonly_fields = ("subscription_updated_at",)

    # Настройки полей при редактировании
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
        (
            "Важные даты",
            {
                "fields": (
                    "last_login",
                    "date_joined"
                )
            }
        ),
        (
            'Маркетинг и Рассылки',
            {
                'fields': (
                    'is_subscribed',
                    'email_status',
                    'subscription_updated_at'  # Теперь работает корректно благодаря readonly_fields
                )
            }
        )
    )

    def get_queryset(self, request):
        """Оптимизация запросов к БД: подгружаем группы разом, избегая проблемы N+1."""
        qs = super().get_queryset(request)
        return qs.prefetch_related('groups')

    @admin.display(description="Группы")
    def get_groups(self, obj):
        """Получение групп пользователей."""
        # Благодаря prefetch_related этот код больше не тормозит базу данных
        return ", ".join([group.name for group in obj.groups.all()])

    @admin.display(description="Подписка", ordering='is_subscribed')
    def is_subscribed_status(self, obj):
        """Отображение согласия на рассылку."""
        if obj.is_subscribed:
            # Используем безопасный format_html БЕЗ префикса f перед строкой
            return format_html('<span style="color: #28a745; font-weight: bold;">{}</span>', "✔ Да")
        return format_html('<span style="color: #dc3545;">{}</span>', "❌ Отписан")

    @admin.display(description="Статус Email", ordering='email_status')
    def email_status_badge(self, obj):
        """Цветной компактный бейдж для статуса валидности почты."""
        colors = {
            'verified': 'background-color: #d4edda; color: #155724; padding: 2px 6px; border-radius: 4px; font-size: 0.85rem;',
            'unverified': 'background-color: #fff3cd; color: #856404; padding: 2px 6px; border-radius: 4px; font-size: 0.85rem;',
            'bounced': 'background-color: #f8d7da; color: #721c24; padding: 2px 6px; border-radius: 4px; font-size: 0.85rem; font-weight: bold;',
        }
        style = colors.get(obj.email_status, '')
        text = obj.get_email_status_display()

        # Передаем динамический стиль и текст в аргументы через запятую
        return format_html('<span style="{}">{}</span>', style, text)