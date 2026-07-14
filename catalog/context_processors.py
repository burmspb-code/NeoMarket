"""Контекстные процессоры приложения каталога.

Обеспечивают автоматическое добавление общих данных (например, меню категорий)
в контекст каждого HTML-шаблона сайта.
"""

from django.conf import settings
from django.core.cache import cache

from catalog.models import Category


def categories_processor(request):
    """
    Автоматически добавляет список всех категорий в контекст каждого шаблона.
    Данные кэшируются в Redis для снижения нагрузки на базу данных.
    """
    # Проверяем глобальный флаг кэширования в settings.py.
    # Если кэш отключен (например, при локальном тестировании), отдаем данные вживую
    if not getattr(settings, "CACHE_ENABLED", False):
        return {"all_categories": Category.objects.all()}

    # Уникальный ключ кэша для меню навигации
    cache_key = "navbar_categories_list"

    # Пытаемся достать готовый список категорий из Redis
    categories_cache = cache.get(cache_key)

    if categories_cache is not None:
        return {"all_categories": categories_cache}

    # Если в Redis пусто — делаем один запрос к БД
    # Важно: принудительно приводим QuerySet к списку через list(),
    # чтобы выполнить запрос и сохранить в Redis готовые объекты, а не ленивый SQL-запрос
    categories = list(Category.objects.all())

    # Безопасно извлекаем время жизни кэша из настроек (по умолчанию 1 час / 3600 секунд)
    timeout = getattr(settings, "CACHE_TIMEOUT", 3600)

    # Записываем вычисленный список в Redis
    cache.set(cache_key, categories, timeout=timeout)

    return {"all_categories": categories}
