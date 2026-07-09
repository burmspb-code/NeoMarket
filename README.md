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

3. **Примените миграции и загрузите демонстрационные данные:**
   Для автоматического создания структуры базы данных, наполнения каталога товарами и старта локального сервера выполните в терминале:

   * **Для Linux / macOS / Git Bash:**
     ```bash
     poetry run python manage.py migrate && poetry run python manage.py loaddata product_fixture && poetry run python manage.py runserver
     ```
   * **Для Windows (PowerShell):**
     ```powershell
     poetry run python manage.py migrate; poetry run python manage.py loaddata product_fixture; poetry run python manage.py runserver
     ```

   > 💡 **Важно:** Фикстуры восстанавливают только записи в базе данных. Чтобы на сайте отображались сами изображения товаров, убедитесь, что папка `media/` присутствует в корне проекта.

