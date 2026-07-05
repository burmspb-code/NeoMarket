"""Представления для управления учетными записями пользователя."""

import secrets

from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View
from django.views.generic.edit import CreateView
from django.core.mail import send_mail

from .forms import CustomUserCreationForm
from .models import CustomUser


class RegisterView(CreateView):
    """Представление для регистрации нового пользователя."""

    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    # Перенаправляем на страницу с уведомлением о проверке почты,
    success_url = reverse_lazy("users:email_confirmation_sent")

    def form_valid(self, form):
        """Представление для регистрации нового пользователя с генерацией токена."""

        # Берем объект пользователя из формы, но пока НЕ сохраняем в базу данных
        user = form.save(commit=False)

        # Генерируем уникальный токен и записываем его в поле модели
        user.token = secrets.token_hex(20)

        # Деактивируем пользователя, пока он не перейдет по ссылке из письма
        user.is_active = False

        # Вызываем super().form_valid, который теперь сохранит пользователя уже вместе с токеном
        response = super().form_valid(form)

        # Получаем хост откуда пришел пользователь
        host = self.request.get_host()

        # Формируем ссылку для подтверждения
        activation_url = f'http://{host}/users/email-confirm/{user.token}/'

        # Отправляем приветственное письмо
        send_mail(
            subject='Подтверждение регистрации',
            message=f'Спасибо за регистрацию! Для активации аккаунта перейдите по ссылке: {activation_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True
        )

        return response


class EmailConfirmView(View):
    """Представление для активации аккаунта по токену из письма."""

    def get(self, request, token):
        # Ищем пользователя с таким токеном, если не нашли — вернем ошибку 404
        user = get_object_or_404(CustomUser, token=token)

        # Активируем пользователя
        user.is_active = True
        # Очищаем токен, чтобы ссылку нельзя было использовать повторно
        user.token = None
        user.save()

        # Перенаправляем на страницу успешного входа
        return redirect("users:login")


class EmailConfirmationSentView(TemplateView):
    """Статическая страница с уведомлением об отправке письма."""

    template_name = "users/email_confirmation_sent.html"