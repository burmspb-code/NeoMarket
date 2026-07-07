"""Маршрутизация для приложения управления пользователями."""

from django.contrib.auth.views import LogoutView
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
    # ИСПРАВЛЕНО: Маршрут использует наш кастомный класс для автоподстановки Email
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
]
