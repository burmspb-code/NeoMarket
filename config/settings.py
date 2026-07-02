import os
from dotenv import load_dotenv
from pathlib import Path


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
    "catalog",
    "library",
    "blog",
    "users",
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
EMAIL_PORT = 465                # Яндекс использует порт 465 для SSL
EMAIL_USE_SSL = True            # Использование SSL вместо TLS (для Яндекса это надежнее)
EMAIL_USE_TLS = False           # Отключаем TLS

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
LOGIN_REDIRECT_URL = "library:books_list"  # Куда направлять после успешного входа
LOGIN_URL = "users:login"  # Куда отправлять неавторизованного пользователя
