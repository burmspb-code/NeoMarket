"""Представления для управления учетными записями пользователя."""

from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm


class RegisterView(CreateView):
    """Представление для регистрации нового пользователя.

    Использует кастомную форму регистрации и перенаправляет пользователя
    на список книг после успешного создания аккаунта.
    Attributes:
        form_class: Класс формы для валидации и создания пользователя.
        template_name (str): Путь к HTML-шаблону страницы для регистрации.
        success_url (str): Путь для перенаправления после успешной регистрации.
    """

    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("library:books_list")

    def form_valid(self, form):
        """Вызывается при успешной валидации данных.
        Сохраняет пользователя в базу данных, выполняет автоматический вход в систему и
        перенаправляет на целевую страницу.
        """
        # Сначала сохраняем пользователя в БД через родительский метод
        response = super().form_valid(form)
        # self.object содержит созданного пользователя — авторизуем его
        login(self.request, self.object)
        return response
