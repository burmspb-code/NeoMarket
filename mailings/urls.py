"""Маршруты для приложения mailings."""

from django.urls import path
from mailings.views import ManualStartMailingView  # <-- Импортируем класс

app_name = 'mailings'

urlpatterns = [
    # ИСПРАВЛЕНО: используем ManualStartMailingView.as_view()
    path('start/<int:mailing_id>/', ManualStartMailingView.as_view(), name='manual_start'),
]
