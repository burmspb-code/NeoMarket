"""Модели для приложения mailings."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


# Create your models here.
class MailingClient(models.Model):
    """Модель получателя рассылки.

    Поля:
        email (EmailField): Адресс электронной почты для рассылок.
        full_name (CharField) Ф.И.О. получателя.
        comment (TextField): Комментарий.
        user (ForeignKey): Связь с зарегистрированными покупателями магазина.
    """
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
        verbose_name="Email",
        help_text="Электронная почта получателя"
    )
    full_name = models.CharField(
        max_length=150,
        verbose_name="Ф.И.О.",
        help_text="Ф.И.О. получателя"
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий",
        help_text="Комментарий"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="mailing_clients",
        verbose_name="Аккаунт получателя"
    )

    class Meta:
        """Класс метаданных."""
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = ['email']

    def __str__(self):
        return f"{self.full_name} {self.email}"


class MailingMessage(models.Model):
    """Модель ссобщения для рассылки.

    Поля:
        message_subject (CharField): Тема письма.
        message_body (TextField): Тело письма.
    """

    message_subject = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        verbose_name="Тема",
        help_text="Введите тему сообщения"
    )
    message_body = models.TextField(
        blank=False,
        null=False,
        verbose_name="Текст сообщения",
        help_text="Введите текст сообщения"
    )

    class Meta:
        """Класс метаданных."""
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['message_subject']

    def __str__(self):
        return f"{self.message_subject}"


class MailingManagement(models.Model):
    """Модель управления рассылками.

    Поля:
        start_time (DateTimeField): Дата и время начала отправки.
        end_time (DateTimeField): Дата и время окончания отправки.
        status (CharField): Статус рассылки.
        message (ForeignKey): Внешний ключ модели MailingMessage (один ко многим).
        recipients (ManyToManyField): Внешний ключ модели MailingClient (многие ко многим).
    Атрибуты:
        STATUS_CHOICES: (list[tuple[str, str]]): Статус рассылки.
    """
    start_time = models.DateTimeField(
        blank=False,
        null=False,
        verbose_name="Дата и время начала отправки",
        help_text="Введите дату и время начала рассылки"
    )
    end_time = models.DateTimeField(
        blank=False,
        null=False,
        verbose_name="Дата и время окончания отправки",
        help_text="Введите дату и время окончания рассылки"
    )
    STATUS_CHOICES: list[tuple[str, str]] = [
        ('created', 'Созданы'),
        ('launched', 'Запущена'),
        ('completed', 'Завершена'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        blank=False,
        null=False,
        verbose_name="Статус рассылки",
        help_text="Выберите статус рассылки"
    )
    message = models.ForeignKey(
        MailingMessage,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="messages",
        verbose_name="Сообщение"
    )
    recipients = models.ManyToManyField(
        MailingClient,
        blank=False,
        related_name="recipients",
        verbose_name="Получатели"
    )

    class Meta:
        """Класс метаданных."""
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ['start_time', 'end_time']

    def __str__(self):
        return f"{self.status}"

    def update_status(self):
        """Динамическое обновление статуса рассылки."""

        # Получение времени начала и окончания текущей рассылки
        mailing_start = self.start_time
        mailing_end = self.end_time

        # Получение текущей даты и времени, bспользуем часовой пояс проекта
        now = timezone.now()

        if mailing_start <= now <= mailing_end:
            self.status = 'launched'
        elif mailing_start > now:
            self.status = 'created'
        else:
            self.status = 'completed'

        # Безопасное обновление поля в базе данных без вызова self.save()
        if self.pk:
            MailingManagement.objects.filter(pk=self.pk).update(status=self.status)

    def clean(self):
        """Валидация на время начала и окончания рассылки."""
        super().clean()

        if self.start_time and self.end_time:
            if self.end_time < self.start_time:
                raise ValidationError(
                    {"end_time": "Время окончания не может быть меньше времени начала рассылки."}
                )


class MailingLog(models.Model):
    """Модель логов для фиксации результатов отправки писем согласно ТЗ.

    Поля:
        mailing (ForeignKey): Связь с конкретной рассылкой.
        attempt_time (DateTimeField): Дата и время попытки отправки.
        status (CharField): Статус попытки (успешно/не успешно).
        server_response (TextField): Ответ почтового сервера или текст ошибки.
    """

    LOG_STATUS_CHOICES: list[tuple[str, str]] = [
        ('success', 'Успешно'),
        ('failed', 'Не успешно'),  # В точности как просит ТЗ (Не успешно)
    ]

    mailing = models.ForeignKey(
        MailingManagement,
        on_delete=models.CASCADE,
        related_name="logs",
        verbose_name="Рассылка"
    )
    attempt_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время попытки"
    )
    status = models.CharField(
        max_length=10,
        choices=LOG_STATUS_CHOICES,
        verbose_name="Статус"
    )
    server_response = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ответ почтового сервера",
        help_text="Здесь лог запишет причину ошибки, если отправка сорвется"
    )

    class Meta:
        verbose_name = "Лог отправки"
        verbose_name_plural = "Логи отправки"
        ordering = ['-attempt_time']

    def __str__(self):
        return f"Попытка #{self.id} для рассылки {self.mailing.id} [{self.get_status_display()}]"
