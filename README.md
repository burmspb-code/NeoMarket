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

## 🚀 Быстрый запуск проекта с демо-данными

Для того чтобы сразу увидеть проект с заполненными товарами и корректными изображениями, выполните следующие шаги:

1. **Подготовьте медиа-файлы:**
   Скопируйте демонстрационные изображения из папки `demo_images/` в локальную директорию `media/photo/` в корне
   проекта (если папки `media` или `photo` не существуют, создайте их).

2. **Примените миграции и загрузите данные:**

    * **Для Linux / macOS / Git Bash:**
        ```bash
        poetry run python manage.py migrate && poetry run python manage.py loaddata product_fixture && poetry run python manage.py runserver
        ```
    * **Для Windows (PowerShell):**
        ```powershell
        poetry run python manage.py migrate; poetry run python manage.py loaddata product_fixture; poetry run python manage.py runserver
        ```

> ⚠️ **Примечание для проверки (Кэширование и Redis):**
> 
> В проекте используется кэширование страниц (декоратор `cache_page`).
> * **Управление кэшем:** В файле `settings.py` добавлена переменная **`CACHE_ENABLED`**. По умолчанию она равна `True`.
    Если вы хотите полностью отключить кэширование для тестов, просто переключите её в `False`.
> * **Автозапуск Redis:** При `CACHE_ENABLED = True` проект автоматически проверяет порт `6379`. Если у вас в системе
    уже запущен Redis, Django подключится к нему сам. Если порт свободен, проект выведет вежливое напоминание в консоль
    о необходимости запуска Redis-сервера, но сам сервер Django при этом продолжит работу.

3. **Готово!** Перейдите по адресу `http://127.0.0` для просмотра сайта.

