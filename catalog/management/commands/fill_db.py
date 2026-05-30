from django.core.management.base import BaseCommand
from catalog.models import Category, Product
from django.core.management import call_command


class Command(BaseCommand):
    """Создание кастомной команды"""
    help = 'Заполняет базу данных начальными данными'

    def handle(self, *args, **options):
        # Очистка базы
        self.stdout.write('Clearing database...')
        Category.objects.all().delete()
        Product.objects.all().delete()

        # Загружаем данные из фикстур
        self.stdout.write('Loading fixture data...')
        call_command('loaddata', 'category_fixture.json')
        call_command('loaddata', 'product_fixture.json')

        # Выводит сообщение в консоль
        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена'))
