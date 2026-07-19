# config/celery.py
import os
from celery import Celery
from kombu.transport.redis import Transport

# Переопределяем параметры подключения прямо в транспортном движке Kombu
# Это отключит RESP3 на самом глубоком системном уровне библиотеки
Transport.connection_errors_blocks = False
Transport.transport_options = {'redis_version': 3}

# Устанавливаем дефолтные настройки Django для celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Читаем конфигурацию из settings.py с префиксом CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически ищем таски (tasks.py) во всех зарегистрированных приложениях
app.autodiscover_tasks()
