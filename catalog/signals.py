from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product, Category


@receiver([post_save, post_delete], sender=Product)
def clear_product_cache(sender, instance, **kwargs):
    """Сбрасывает кэш списков сервисного слоя и карточки товара при изменении продукта."""

    # Сбрасываем кэш детальной карточки этого товара
    cache.delete(f"product_detail_{instance.slug}")

    # Сбрасываем кэш общего списка товаров из сервиса get_products_cache()
    cache.delete("products_list")

    # Сбрасываем кэш конкретной категории, к которой привязан товар
    if instance.category:
        cache.delete(f"products_category_{instance.category.slug}")


@receiver([post_save, post_delete], sender=Category)
def clear_category_cache(sender, instance, **kwargs):
    """Сбрасывает кэш категории и общего меню навигации при изменении её структуры."""
    # 1. Очищаем список товаров измененной категории из сервисного слоя
    cache.delete(f"products_category_{instance.slug}")

    # 2. ИСПРАВЛЕНИЕ: Очищаем закешированный список категорий для выпадающего меню navbar
    # Стираем тот самый ключ, который мы создали в context_processors.py
    cache.delete("navbar_categories_list")
