"""Представления для управления учетными записями пользователя."""

from django.conf import settings
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.core.mail import send_mail
from .forms import CustomUserCreationForm


class RegisterView(CreateView):
    """Представление для регистрации нового пользователя."""

    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("catalog:catalog_list")

    def form_valid(self, form):
        """Вызывается при успешной валидации данных."""
        # super().form_valid сохраняет юзера в базу и создает объект HttpResponseRedirect
        response = super().form_valid(form)

        # Логиним пользователя (self.object уже создан родительским методом)
        login(self.request, self.object)

        # Отправляем приветственное письмо
        send_mail(
            'Добро пожаловать на NeoMarket!',
            'Спасибо, что зарегистрировались на нашем сайте!',
            settings.DEFAULT_FROM_EMAIL,
            [self.object.email],
            fail_silently=True
        )

        return response
