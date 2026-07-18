"""Представления для управления учетными записями пользователя с безопасными токенами."""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import TemplateView, View, UpdateView
from django.views.generic.edit import CreateView

from .forms import CustomUserCreationForm, UserProfileForm
from .models import CustomUser


class CustomLoginView(LoginView):
    """Кастомное представление входа для автоматической подстановки email."""

    template_name = "users/login.html"

    def get_initial(self):
        initial = super().get_initial()
        # Вытаскиваем email из GET-параметра ?email=...
        email_from_url = self.request.GET.get("email")
        if email_from_url:
            # В стандартной форме аутентификации поле логина называется 'username'
            initial["username"] = email_from_url
        return initial


class RegisterView(CreateView):
    """Представление для регистрации нового пользователя с безопасным временным токеном."""

    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:email_confirmation_sent")

    def form_valid(self, form):
        # Открываем транзакцию: если письмо не уйдёт, пользователь не создастся в БД
        with transaction.atomic():
            # Создаем неактивного пользователя
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Генерируем uid и токен
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # Собираем ссылку активации
            relative_url = reverse(
                "users:email_confirm", kwargs={"uidb64": uid, "token": token}
            )
            scheme = "https" if self.request.is_secure() else "http"
            host = self.request.get_host()
            activation_url = f"{scheme}://{host}{relative_url}"

            try:
                # Отправляем письмо с обязательной генерацией исключения при сбое
                send_mail(
                    subject="Подтверждение регистрации",
                    message=f"Спасибо за регистрацию! Ссылка для активации: {activation_url}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                # Если отправка прошла успешно, перенаправляем на success_url
                return redirect(self.success_url)

            except Exception:
                # Показываем понятную ошибку пользователю на фронтенде
                messages.error(
                    self.request,
                    "Произошла ошибка при отправке письма с подтверждением. "
                    "Пожалуйста, проверьте правильность ввода email или попробуйте позже.",
                )

                # Отменяем сохранение пользователя в базе данных
                transaction.set_rollback(True)

                # Возвращаем пользователя на форму с сохраненными данными полей
                return self.render_to_response(self.get_context_data(form=form))


class EmailConfirmView(View):
    """Представление для активации аккаунта по uid и токену."""

    def get(self, request, uidb64, token):
        try:
            # Используем корректное имя модели CustomUser вместо User
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        # Проверяем, существует ли пользователь и валиден ли токен (не истек ли срок)
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.email_status = 'verified' # Меняем статус почты
            user.save()

            # Добавляем красивое уведомление, которое отобразится на странице входа
            messages.success(
                request,
                "Ваш аккаунт успешно активирован! Пожалуйста, войдите в систему.",
            )

            # Формируем URL для страницы входа с GET-параметром email
            login_url = reverse("users:login")
            return redirect(f"{login_url}?email={user.email}")
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
