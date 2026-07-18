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
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password"),  # Заменили 'username' на 'email'
            },
        ),
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
        # Насыщенные контрастные цвета, которые отлично читаются на темном фоне
        colors = {
            'verified': 'background-color: rgba(40, 167, 69, 0.2); color: #2ecc71; border: 1px solid rgba(40, 167, 69, 0.4); padding: 3px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; display: inline-block;',
            'unverified': 'background-color: rgba(255, 193, 7, 0.15); color: #f1c40f; border: 1px solid rgba(255, 193, 7, 0.3); padding: 3px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; display: inline-block; white-space: nowrap;',
            'bounced': 'background-color: rgba(220, 53, 69, 0.2); color: #e74c3c; border: 1px solid rgba(220, 53, 69, 0.4); padding: 3px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: bold; display: inline-block;',
        }

        style = colors.get(obj.email_status, 'color: #fff;')
        text = obj.get_email_status_display()

        # format_html автоматически защищает от XSS и корректно рендерит тег
        return format_html('<span style="{}">{}</span>', style, text)