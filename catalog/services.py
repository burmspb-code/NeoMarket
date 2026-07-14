"""Сервисный слой для приложения каталога товаров.

Содержит бизнес-логику, вынесенную из представлений (views),
а также функции для оптимизации запросов и кэширования данных.
"""

from django.conf import settings
from django.core.cache import cache

from catalog.models import Product


def get_products_cache():
    """Кеширование списка продуктов с динамическим таймаутом."""

    def get_optimized_products():
        """Получение списка опубликованных продуктов."""
        return (
            Product.objects.filter(published=True)
            .select_related("category")
            .prefetch_related("images")
            .order_by("id")
        )

    if not getattr(settings, "CACHE_ENABLED", False):
        return get_optimized_products()

    key_prod = "products_list"
    products_cache = cache.get(key_prod)

    if products_cache is not None:
        return products_cache

    products = get_optimized_products()

    # Безопасное извлечение CACHE_TIMEOUT
    timeout = getattr(settings, "CACHE_TIMEOUT", 60)

    cache.set(key_prod, products, timeout=timeout)
    return products


def get_products_by_category_cache(category_id):
    """Кеширование товаров выбранной категории."""

    def get_optimized_category_products():
        """Получение продуктов из категории."""
        return (
            Product.objects.filter(category_id=category_id, published=True)
            .select_related("category")
            .prefetch_related("images")
            .order_by("id")
        )

    if not getattr(settings, "CACHE_ENABLED", False):
        return get_optimized_category_products()

    # Формируем уникальный ключ кэша для КАЖДОЙ категории отдельно!
    key_prod = f"products_category_{category_id}"
    products_cache = cache.get(key_prod)

    if products_cache is not None:
        return products_cache

    products = get_optimized_category_products()
    timeout = getattr(settings, "CACHE_TIMEOUT", 60)
    cache.set(key_prod, products, timeout=timeout)
    return products
