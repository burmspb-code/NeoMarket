"""Формы для аутентификации и управления пользователями."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django_countries import countries
# ИСПРАВЛЕНО: Импортируем поле формы для корректной валидации телефонов мира
from phonenumber_field.formfields import PhoneNumberField

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Создание кастомной формы для регистрации пользователя."""

    # ИСПРАВЛЕНО: Теперь поле формы соответствует полю модели.
    # Оно само проверяет корректность кодов стран, плюсов и пробелов.
    phone_number = PhoneNumberField(
        required=False,
        help_text="Введите номер телефона (необязательное поле).",
    )

    # Отключаем форму для интеграции пароля на других сервисах
    usable_password = None

    class Meta(UserCreationForm.Meta):
        """Метаданные формы. Привязка к модели CustomUser и определение полей."""

        model = CustomUser
        # Поля разделены для предотвращения ложного автозаполнения браузером
        fields = ("email", "first_name", "last_name", "country", "phone_number", "avatar")

    def __init__(self, *args, **kwargs):
        """Настройка полей после инициализации формы."""
        super().__init__(*args, **kwargs)

        # ИСПРАВЛЕНО: Явно меняем текстовый виджет поля страны на выпадающий список Select.
        # Без этой строки передача choices ниже приведет к ошибкам рендеринга.
        self.fields["country"].widget = forms.Select()
        self.fields["country"].choices = [("", "------")] + list(countries)

        # Добавляем класс Bootstrap ко всем полям, включая поля паролей
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})

        # Отключаем автозаполнение для телефона, чтобы туда не падал Email
        self.fields["phone_number"].widget.attrs.update({
            "autocomplete": "tel"
        })

    # УДАЛЕНО: Метод clean_phone_number больше не нужен,
    # так как PhoneNumberField автоматически и гораздо лучше валидирует любые номера.
