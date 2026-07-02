"""Маршрутизация для приложения управления пользователями."""

from django.urls import path
from .views import RegisterView
from django.contrib.auth.views import LoginView, LogoutView

# Пространство имен для URL-адресов приложения
app_name = "users"

urlpatterns = [
    # Страница регистрации нового пользователя
    path("register/", RegisterView.as_view(), name="register"),
    # Страница аутентификации
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    # Выход после аутентификации и перенаправления на список книг
    path("logout/", LogoutView.as_view(next_page="library:books_list"), name="logout"),
]
