"""Маршруты для приложения mailings."""

from django.urls import path
from mailings.views import ManualStartMailingView, MailingDashboardView, MailingCreateView

app_name = 'mailings'

urlpatterns = [
    # Станица запуска рассылки через админ-панель
    path('start/<int:mailing_id>/', ManualStartMailingView.as_view(), name='manual_start'),
    # Страница дашборда
    path('dashboard/', MailingDashboardView.as_view(), name='dashboard'),
    # Страница созданая рассылки
    path('create/', MailingCreateView.as_view(), name='create'),
]
