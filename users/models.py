from django.db import models
from django.contrib.auth.models import AbstractUser


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

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
