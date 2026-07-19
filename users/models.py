from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    """Кастомная модель пользователя использующая поле email в качестве основого идентификатора.
    Поля:
        username (CharField): Стандартное поле Django, оставлено для совместимости.
        email (EmailField): Уникальный адрес электронной почты, используется для входа.
        phone_number (CharField): Номер телефона пользователя, необязательное поле.
        country (CountryField): Страна проживания пользователя, необязательное поле.
        avatar (ImageField): Изображение профиля, необязательное поле.
        is_subscribed (BooleanField): Согласие на получение рассылок.
        email_status (CharField): Статус почты пользователя.
        subscription_updated_at (DateTimeField): Дата изменения статуса подписки.
    Атрибуты:
        EMAIL_STATUS_CHOICES (list[tuple[str, str]]): Статус валидности email.
        USERNAME_FIELD (str): Указывает на email для аутентификации.
        REQUIRED_FIELDS (list): Список обязательных полей для создания superuser (['username']).
    """

    username = None
    email = models.EmailField(unique=True, verbose_name="Email")
    phone_number = PhoneNumberField(
        blank=True,
        null=True,
        unique=True,
        verbose_name="Номер телефона",
        help_text="Введите номер телефона",
    )
    country = CountryField(
        blank=True,
        null=True,
        verbose_name="Страна",
        help_text="Выберите страну проживания",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        null=True,
        blank=True,
        verbose_name="Аватар",
        help_text="Загрузите аватар",
    )
    is_subscribed = models.BooleanField(
        default=True, verbose_name="Согласен на получение маркетинговых рассылок"
    )
    # Статус валидности email для защиты репутации домена
    EMAIL_STATUS_CHOICES: list[tuple[str, str]] = [
        ("unverified", "Не подтвержден"),
        ("verified", "Подтвержден"),
        ("bounced", "Ошибка доставки (Bounced)"),
    ]
    email_status = models.CharField(
        max_length=15,
        choices=EMAIL_STATUS_CHOICES,
        default="unverified",
        verbose_name="Статус Email",
    )
    # Дата изменения статуса подписки (полезно для аналитики)
    subscription_updated_at = models.DateTimeField(
        default=timezone.now, verbose_name="Дата изменения подписки"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        """Переопределение метода сохранения пользователя."""
        # Если объект уже существует в базе данных (это обновление, а не создание)
        if self.pk:
            old_user = CustomUser.objects.get(pk=self.pk)
            # Проверяем, изменился ли флаг подписки
            if old_user.is_subscribed != self.is_subscribed:
                self.subscription_updated_at = timezone.now()

        super().save(*args, **kwargs)
