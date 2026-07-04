import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    """Консольная команда для безопасного создания суперпользователя из переменных окружения (.env)."""

    help = "Идемпотентно создает администратора системы, используя Email в качестве идентификатора."

    def handle(self, *args, **options):
        """Безопасно создает суперпользователя на основе данных из .env, предотвращая дублирование учетных записей при повторном запуске."""
        User = get_user_model()

        # Безопасное получение данных из окружения
        email = os.environ.get("ADMIN_EMAIL", "default_admin@example.com")
        password = os.environ.get("ADMIN_PASSWORD")

        if not password:
            self.stdout.write(
                self.style.ERROR("Ошибка: В файле .env не задана переменная ADMIN_PASSWORD")
            )
            return

        # Использование get_or_create предотвращает падение при повторном запуске
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": "admin",
                "last_name": "admin",
                "is_staff": True,
                "is_superuser": True,
            }
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f"Успешно создан админ: {email}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"Пользователь {email} уже существует в базе данных.")
            )
