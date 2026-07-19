@echo off
chcp 65001 > nul
title Панель запуска NeoMarket

echo =======================================================================
echo           Автоматический запуск интернет-магазина NeoMarket
echo =======================================================================
echo.

:: Шаг 1: Проверка файла окружения
if not exist .env (
    echo [NeoMarket] Файл .env не найден. Создаю локальный .env из шаблона...
    copy .env.sample .env > nul
)

:: Шаг 2: Установка зависимостей
echo [NeoMarket] 1. Проверяю и устанавливаю зависимости через Poetry...
call poetry install
if %errorlevel% neq 0 (
    echo [Ошибка] Не удалось установить зависимости. Убедитесь, что Poetry установлен.
    pause
    exit /b
)

:: Шаг 3: Миграции
echo [NeoMarket] 2. Накатываю миграции базы данных...
call poetry run python manage.py migrate

:: Шаг 4: Загрузка фикстур (Группы, Товары, Блог, Рассылки)
echo [NeoMarket] 3. Загружаю группы пользователей и права доступа...
call poetry run python manage.py loaddata groups_and_permissions

echo [NeoMarket] 4. Загружаю демонстрационные товары каталога...
call poetry run python manage.py loaddata product_fixture

echo [NeoMarket] 5. Загружаю статьи и публикации блога...
call poetry run python manage.py loaddata blog_fixture

echo [NeoMarket] 6. Загружаю тестовые данные маркетинговых рассылок...
call poetry run python manage.py loaddata mailings_fixture

:: Шаг 5: Инициализация Суперпользователя вашей кастомной командой
echo [NeoMarket] 7. Запускаю безопасную инициализацию Администратора...
call poetry run python manage.py createadmin

:: Шаг 6: Запуск инфраструктуры в параллельных открытых окнах
echo [NeoMarket] 8. Запускаю фоновые службы и веб-сервер...
echo.
echo -----------------------------------------------------------------------
echo [УСПЕХ] Инфраструктура разворачивается!
echo.
echo Сайт будет доступен по адресу: http://127.0.0.1:8000
echo Панель администратора: http://127.0.0
echo.
echo Данные для входа под Администратором:
echo Логин (Email): admin@neomarket.local
echo Пароль: admin
echo -----------------------------------------------------------------------
echo.

:: Запускаем три компонента в отдельных открытых окнах, чтобы наставник видел логи
start "NeoMarket: Django Веб-сайт" poetry run python manage.py runserver
start "NeoMarket: Celery Worker (Отправка писем)" poetry run celery -A config worker --loglevel=info --pool=threads
start "NeoMarket: Celery Beat (Планировщик времени)" poetry run celery -A config beat --loglevel=info

pause
