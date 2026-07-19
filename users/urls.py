"""Маршрутизация для приложения управления пользователями."""

from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from django.urls import path

# Импортируем модуль views целиком, чтобы избежать проблем с импортами
from . import views

# Пространство имен для URL-адресов приложения
app_name = "users"

urlpatterns = [
    # Маршрут для регистрации нового пользователя (template_name убран, так как он есть во views)
    path(
        "register/",
        views.RegisterView.as_view(),
        name="register",
    ),
    # Маршрут для входа (использует наш кастомный класс для автоподстановки Email)
    path("login/", views.CustomLoginView.as_view(), name="login"),
    # Маршрут для выхода (использует стандартный LogoutView)
    path("logout/", LogoutView.as_view(next_page="catalog:home"), name="logout"),
    # Маршрут для показа сообщения «Проверьте почту»
    path(
        "email-confirmation-sent/",
        views.EmailConfirmationSentView.as_view(),
        name="email_confirmation_sent",
    ),
    # Динамический маршрут, который принимает uid и токен из письма
    path(
        "email-confirm/<str:uidb64>/<str:token>/",
        views.EmailConfirmView.as_view(),
        name="email_confirm",
    ),
    # Маршрут для редактирования профиля
    path("profile/edit/", views.ProfileUpdateView.as_view(), name="profile_edit"),
    # Маршрут для восстановлния пароля
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="users/password_reset_form.html",
            email_template_name="users/password_reset_email.html",
            success_url="/users/password-reset/done/",
        ),
        name="password_reset",
    ),
    # Страница "Проверьте почту" (после успешного ввода Email)
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    # Ссылка из письма. Форма ввода НОВОГО пароля (uidb64 и token генерирует Django)
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url="/users/password-reset/complete/",
        ),
        name="password_reset_confirm",
    ),
    # Страница успешного изменения пароля
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]
