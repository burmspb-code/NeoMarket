from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "catalog"

    def ready(self):
        # Импортируем сигналы, чтобы Django начал их слушать
        import catalog.signals  # noqa: F401
