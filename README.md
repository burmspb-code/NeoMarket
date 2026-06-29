# NeoMarket
Проект интернет-магазина замков и фурнитуры.

## Инструкция по установке

Для работы проекта требуется менеджер зависимостей [Poetry](https://python-poetry.org/).

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/burmspb-code/NeoMarket.git
   cd NeoMarket
   ```

2. **Установите зависимости:**
   ```bash
   poetry install
   ```

3. **Запустите проект с демонстрационными данными:**
   Для применения миграций, загрузки каталога (категорий, товаров и галереи изображений) и старта локального сервера выполните в терминале:

   * **Для Linux / macOS / Git Bash:**
     ```bash
     poetry run python manage.py migrate && poetry run python manage.py loaddata catalog/fixtures/category_fixture.json catalog/fixtures/product_fixture.json catalog/fixtures/product_images_dump.json && poetry run python manage.py runserver
     ```
   * **Для Windows (PowerShell):**
     ```powershell
     poetry run python manage.py migrate; poetry run python manage.py loaddata catalog/fixtures/category_fixture.json catalog/fixtures/product_fixture.json catalog/fixtures/product_images_dump.json; poetry run python manage.py runserver
     ```

   > 💡 **Важно:** Фикстуры восстанавливают только записи в базе данных. Чтобы на сайте отображались сами изображения товаров и текстуры, убедитесь, что папка `media/` скопирована в корень проекта.

