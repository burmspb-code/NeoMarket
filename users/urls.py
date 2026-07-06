"""Маршрутизация для приложения управления пользователями."""
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import RegisterView, EmailConfirmView, EmailConfirmationSentView

# Пространство имен для URL-адресов приложения
app_name = "users"

urlpatterns = [
    # Маршрут для регистрации нового пользователя
    path("register/", RegisterView.as_view(template_name="users/register.html"), name="register"),
    # Маршрут для аутентификации пользователя
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    # Маршрут для перенаправления после успешной аутентификации пользователя
    path("logout/", LogoutView.as_view(next_page="catalog:home"), name="logout"),
    # Маршрут для показа сообщения «Проверьте почту»
    path("email-confirmation-sent/", EmailConfirmationSentView.as_view(), name="email_confirmation_sent"),
    # Динамический маршрут, который принимает uid и токен из письма
    path('email-confirm/<str:uidb64>/<str:token>/', EmailConfirmView.as_view(), name='email_confirm'),
]
