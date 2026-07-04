from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    """Кастомная модель пользователя использующая поле email в качестве основого идентификатора.
    Поля:
        email (EmailField): Уникальный адрес электронной почты, используется для входа.
        phone_number (CharField): Номер телефона пользователя, необязательное поле.
        avatar (ImageField): Изображение профиля, необязательное поле.
        username (CharField): Стандартное поле Django, оставлено для совместимости.
    Атрибуты:
        USERNAME_FIELD (str): Указывает на email для аутентификации.
        REQUIRED_FIELDS (list): Список обязательных полей для создания superuser (['username']).
    """
    username = None
    email = models.EmailField(unique=True, verbose_name='Email')
    phone_number = PhoneNumberField(
        blank=True,
        null=True,
        unique=True,
        verbose_name='Номер телефона',
        help_text='Введите номер телефона'
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        null=True,
        blank=True,
        verbose_name = 'Аватар',
        help_text = 'Загрузите аватар'
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользлватели'

    def __str__(self):
        return self.email
