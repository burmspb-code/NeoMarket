# NeoMarket
Проект интернет-магазина замков и фурнитуры.

## Инструкция по установке

Для работы проекта требуется менеджер зависимостей [Poetry](https://python-poetry.org/).

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/burmspb-code/NeoMarket.git
   ```

2. **Установите зависимости:**
   ```bash
   poetry install
   ```

3. **Запустите проект с демонстрационными данными:**
   Для автоматического применения миграций, загрузки актуальной базы категорий/товаров и запуска локального сервера выполните в терминале следующую команду:
   ```bash
   poetry run python manage.py migrate && poetry run python manage.py loaddata catalog/fixtures/category_fixture.json catalog/fixtures/product_fixture.json && poetry run python manage.py runserver
   ```
