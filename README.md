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
> В проекте используется кэширование страниц (декоратор `cache_page`). Для его корректной работы требуется запущенный
> Redis-сервер на стандартном порту `6379`. Если у вас в системе уже работает Redis, проект подключится к нему
> автоматически. Если Redis выключен, проект запустится, но выведет напоминание о необходимости его включения в консоль.

3. **Готово!** Перейдите по адресу `http://127.0.0` для просмотра сайта.

