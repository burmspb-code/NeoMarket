"""Представления для управления учетными записями пользователя с безопасными токенами."""

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import TemplateView, View
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from .forms import UserProfileForm

from .forms import CustomUserCreationForm
from .models import CustomUser


class RegisterView(CreateView):
    """Представление для регистрации нового пользователя с безопасным временным токеном."""

    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:email_confirmation_sent")

    def form_valid(self, form):
        # Сохраняем пользователя, но делаем его неактивным
        user = form.save(commit=False)
        user.is_active = False
        user.save()  # Сохраняем в БД, так как для генерации токена нужен ID пользователя

        # Кодируем ID пользователя в base64 (безопасно для URL)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Генерируем безопасный криптографический токен со сроком действия
        token = default_token_generator.make_token(user)

        # Автоматически определяем протокол (http или https) и хост
        scheme = "https" if self.request.is_secure() else "http"
        host = self.request.get_host()

        # Формируем ссылку, передавая и uid, и токен
        activation_url = f"{scheme}://{host}/users/email-confirm/{uid}/{token}/"

        # Отправляем письмо
        send_mail(
            subject="Подтверждение регистрации",
            message=f"Спасибо за регистрацию! Для активации аккаунта перейдите по ссылке: {activation_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

        return redirect(self.success_url)


class EmailConfirmView(View):
    """Представление для активации аккаунта по uid и токену."""

    def get(self, request, uidb64, token):
        try:
            # Декодируем ID пользователя обратно из base64
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        # Проверяем, существует ли пользователь и валиден ли токен (не истек ли срок)
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect("users:login")
        else:
            # Если токен устарел или неверный, показываем страницу с ошибкой
            return render(request, "users/email_confirmation_failed.html")


class EmailConfirmationSentView(TemplateView):
    """Статическая страница с уведомлением об отправке письма."""

    template_name = "users/email_confirmation_sent.html"


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования профиля текущего пользователя."""

    model = CustomUser
    form_class = UserProfileForm
    template_name = "users/profile_edit.html"

    # Куда перенаправить пользователя после успешного сохранения профиля
    success_url = reverse_lazy("catalog:home")

    def get_object(self, queryset=None):
        """Редактируем строго того пользователя, который сейчас авторизован."""
        return self.request.user
