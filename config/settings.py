import redis
from redis.exceptions import RedisError

# Патч №1: Форсируем протокол RESP2 для всех соединений
original_init = redis.connection.Connection.__init__
def patched_init(self, *args, **kwargs):
    kwargs['protocol'] = 2
    original_init(self, *args, **kwargs)
redis.connection.Connection.__init__ = patched_init

# Патч №2: Глушим проверку Maintenance Notifications, которая требует RESP3
def patched_configure_maintenance_notifications(self, *args, **kwargs):
    self._maint_notifications_pool_handler = None
redis.connection.Connection._configure_maintenance_notifications = patched_configure_maintenance_notifications


import os
from pathlib import Path

from dotenv import load_dotenv
from redis import ConnectionPool

# Путь к корневой директории проекта: BASE_DIR / 'папка'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Загрузка переменных окружения из файла .env
load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)

# ПРЕДУПРЕЖДЕНИЕ О БЕЗОПАСНОСТИ: храните секретный ключ в тайне на продакшене!
SECRET_KEY = os.getenv("SECRET_KEY")

# ПРЕДУПРЕЖДЕНИЕ О БЕЗОПАСНОСТИ: не запускайте проект с включенной отладкой на продакшене!
DEBUG = True

# Разрешенные хосты для работы приложения
ALLOWED_HOSTS = ["*"]

# Определение приложений проекта
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Сторонние библиотеки
    "phonenumber_field",  # Модуль валидации номера телефона
    "django_countries",  # Модуль выбора страны из выпадающего списка
    "django_recaptcha",  # Модуль капчи
    "debug_toolbar", # Панель для отладки сайта
    'django_celery_beat',  # Добавляем планировщик в базу

    # Локальные приложения проекта
    "catalog",
    "library",
    "blog",
    "users",
    "mailings",
]

# Промежуточное программное обеспечение (Middleware)
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# Главный файл конфигурации URL
ROOT_URLCONF = "config.urls"

# Конфигурация шаблонизатора
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # Контекстные процессоры Django для шаблонов
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "catalog.context_processors.categories_processor",
            ],
        },
    },
]

# Точка входа для WSGI-серверов
WSGI_APPLICATION = "config.wsgi.application"

# Настройки базы данных PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# Валидаторы паролей для безопасности учетных записей
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Языковые и региональные настройки
LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True


# Настройки статических файлов (CSS, JavaScript, изображения)
STATIC_URL = "/static/"

STATICFILES_DIRS = [BASE_DIR / "static"]

# Настройки медиа-файлов (загружаемые пользователями файлы)
MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

# Использование SMTP для отправки писем
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Конфигурация SMTP Яндекс
EMAIL_HOST = "smtp.yandex.ru"
EMAIL_PORT = 465  # Яндекс использует порт 465 для SSL
EMAIL_USE_SSL = True  # Использование SSL вместо TLS (для Яндекса это надежнее)
EMAIL_USE_TLS = False  # Отключаем TLS

# Логин и пароль приложения почты
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")

# 16-значный пароль приложения почты
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

# Email отправителя по умолчанию
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

# Email для получения уведомлений о просмотрах
EMAIL_ADMIN_NOTIFICATION = os.getenv("EMAIL_ADMIN_NOTIFICATION")

# Подключение кастомной модели пользователя
AUTH_USER_MODEL = "users.CustomUser"

# Настройки перенаправления для системы аутентификации
LOGIN_REDIRECT_URL = "catalog:home"  # Куда направлять после успешного входа
LOGIN_URL = "users:login"  # Куда отправлять неавторизованного пользователя
LOGOUT_REDIRECT_URL = "catalog:home"  # Куда направлять после успешного выхода

# Регион по умолчанию для валидации номеров (ISO 3166-1 alpha-2)
PHONENUMBER_DEFAULT_REGION = "RU"

# Время жизни токена для восстановления пароля и активации аккаунта (24 часа)
PASSWORD_RESET_TIMEOUT = 24 * 60 * 60  # 86400 секунд

# Ключи Google reCAPTCHA v2 (для рабочей среды замените на свои из Google Console)
RECAPTCHA_PUBLIC_KEY = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"  # Публичный ключ
RECAPTCHA_PRIVATE_KEY = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"  # Секретный ключ

# Отключение ошибки при локальной разработке с тестовыми ключами:
SILENCED_SYSTEM_CHECKS = ["django_recaptcha.recaptcha_test_key_error"]

# Кеширование проекта
CACHE_ENABLED = True

CACHE_TIMEOUT = 60

if CACHE_ENABLED:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379"),
            "OPTIONS": {
                "protocol": 2,  # Говорим Django: "Общайся со старым Redis через старый протокол"
            },
        }
    }

# Настройте внутренние IP, чтобы панель Django-debug-tools была видна на локальном компьютере
INTERNAL_IPS = [
    "127.0.0.1",
]

# 1. Возвращаем чистые классические URL без параметров в строке
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'

# 2. Переопределяем пул соединений для БРОКЕРА
# Это заставит внутренний драйвер принудительно использовать старый протокол RESP2
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'redis_version': 3,
    'connection_pool_cls': ConnectionPool,
    'connection_pool_kwargs': {
        'protocol': 2
    }
}

# 3. Переопределяем пул соединений для БЭКЕНДА РЕЗУЛЬТАТОВ
CELERY_REDIS_BACKEND_TRANSPORT_OPTIONS = {
    'redis_version': 3,
    'connection_pool_cls': ConnectionPool,
    'connection_pool_kwargs': {
        'protocol': 2
    }
}

# Остальные стандартные параметры вашего проекта
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'