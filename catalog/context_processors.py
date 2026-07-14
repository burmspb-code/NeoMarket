from catalog.models import Category


def categories_processor(request):
    """Автоматически добавляет список всех категорий в контекст каждого шаблона."""
    return {"all_categories": Category.objects.all()}
