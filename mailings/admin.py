"""Настройки административной панели для управления рассылками."""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from mailings.models import MailingClient, MailingMessage, MailingManagement, MailingLog


@admin.register(MailingClient)
class MailingClientAdmin(admin.ModelAdmin):
    """Панель администратора для управления получателями рассылок."""
    # Поля, которые будут отображаться в таблице
    list_display = ("email", "full_name", "comment", "user")

    # Поля, по которым работает поиск
    search_fields = ("email", "full_name", "comment")

    # Поля, на которые можно нажать для перехода к редактированию
    list_display_links = ("email",)


@admin.register(MailingMessage)
class MailingMessageAdmin(admin.ModelAdmin):
    """Панель администратора для управления шаблонами сообщений."""
    # Поля, которые будут отображаться в таблице
    list_display = ("message_subject", "message_body")

    # Поля, по которым работает поиск
    search_fields = ("message_subject",)

    # Поля, на которые можно нажать для перехода к редактированию
    list_display_links = ("message_subject",)


@admin.register(MailingManagement)
class MailingManagementAdmin(admin.ModelAdmin):
    """Панель администратора для настройки параметров и расписания рассылок."""
    # Поля, которые будут отображаться в таблице
    list_display = ("message", "status", "start_time", "end_time")

    # Поля, по которым работает поиск
    search_fields = ("start_time", "end_time", "status")

    # Поля, на которые можно нажать для перехода к редактированию
    list_display_links = ("status",)

    # Добавляем поле кнопки только для чтения на страницу редактирования
    readonly_fields = ("start_button",)

    @admin.display(description="Действие")
    def start_button(self, obj):
        """Генерация кнопки ручного запуска для таблицы и формы редактирования."""
        if obj.pk:
            url = reverse('mailings:manual_start', kwargs={'mailing_id': obj.pk})
            return format_html(
                '<a class="button" style="background-color: #28a745; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none;" href="{}">▶ Запустить сейчас</a>',
                url
            )
        return "Сначала сохраните рассылку"


@admin.register(MailingLog)
class MailingLoggingAdmin(admin.ModelAdmin):
    """Панель администратора для просмотра логов рассылок."""

    # Поля в удобном порядке: сначала время и статус, затем ответ сервера
    list_display = ("attempt_time", "status", "server_response")

    # Переносим кликабельность на время попытки, чтобы заходить в детали лога
    list_display_links = ("attempt_time",)

    # Ищем только по тексту ответа сервера и статусу.
    search_fields = ("status", "server_response")

    # Добавляем боковые фильтры — для логов это самый удобный инструмент (по дням и статусам)
    list_filter = ("status", "attempt_time")

    # Запрещаем редактирование логов прямо из админки (логи должны быть неизменяемыми)
    readonly_fields = ("attempt_time", "status", "server_response")
