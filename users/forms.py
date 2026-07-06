"""Формы для аутентификации и управления пользователями."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django_countries import countries
from phonenumber_field.formfields import PhoneNumberField
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Создание кастомной формы для регистрации пользователя."""

    # 1. Объявляем капчу строго как отдельное поле класса
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox(),
        error_messages={
            'required': 'Пожалуйста, подтвердите, что вы не робот.'
        }
    )

    phone_number = PhoneNumberField(
        required=False,
        help_text="Введите номер телефона (необязательное поле).",
    )

    class Meta:
        model = CustomUser
        # 2. ВНИМАНИЕ: Сюда мы пишем только реальные поля модели CustomUser.
        # Поле 'captcha' сюда вносить НЕЛЬЗЯ, иначе Django создаст дубликат!
        fields = ("email", "first_name", "last_name", "country", "phone_number", "avatar")

    def __init__(self, *args, **kwargs):
        """Настройка полей после инициализации формы."""
        super().__init__(*args, **kwargs)

        # Переопределяем поле страны
        self.fields["country"].widget = forms.Select()
        self.fields["country"].choices = [("", "------")] + list(countries)

        # 3. Добавляем Bootstrap-классы, аккуратно обходя капчу
        for field_name, field in self.fields.items():
            if field_name != 'captcha':
                field.widget.attrs.update({"class": "form-control"})

        # Отключаем автозаполнение для телефона
        self.fields["phone_number"].widget.attrs.update({
            "autocomplete": "tel"
        })
