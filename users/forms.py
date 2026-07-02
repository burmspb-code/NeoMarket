"""Формы для аутентификации и управления пользователями."""

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Создание кастомной формы для регистрации пользователя."""

    phone_number = forms.CharField(
        max_length=15,
        required=False,
        help_text="Введите номер телефона (необязательное поле).",
    )
    username = forms.CharField(max_length=50, required=True)
    # Отключаем форму для интеграции паролья на других сервисах
    usable_password = None

    class Meta(UserCreationForm.Meta):
        """Метаданные формы. Привязка к модели CustomUser и определение полей."""

        model = CustomUser
        fields = ("email", "username", "first_name", "last_name", "phone_number")

    def clean_phone_number(self):
        """Валидация номера телефона. Разрешены только цифры."""
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError("Номер телефона должен содержать только цифры.")

        return phone_number
