#!/bin/bash

echo "======================================================================="
echo "          Автоматический запуск интернет-магазина NeoMarket"
echo "======================================================================="
echo

# 1. Проверка .env
if [ ! -f .env ]; then
    echo "[NeoMarket] Файл .env не найден. Создаю локальный .env из шаблона..."
    cp .env.sample .env
fi

# 2. Зависимости
echo "[NeoMarket] 1. Установка зависимостей через Poetry..."
poetry install

# 3. База данных и миграции
echo "[NeoMarket] 2. Применение миграций..."
poetry run python manage.py migrate

# 4. Загрузка фикстур
echo "[NeoMarket] 3. Загрузка групп пользователей и прав доступа..."
poetry run python manage.py loaddata groups_and_permissions

echo "[NeoMarket] 4. Загрузка демонстрационных товаров..."
poetry run python manage.py loaddata product_fixture

echo "[NeoMarket] 5. Загрузка тестовых данных маркетинговых рассылок..."
poetry run python manage.py loaddata mailings_fixture

# 5. Кастомная команда создания админа
echo "[NeoMarket] 6. Безопасная инициализация Главного Администратора..."
poetry run python manage.py createadmin

# 6. Запуск параллельных процессов
echo "[NeoMarket] 7. Запуск веб-сервера и роботов Celery..."

# Функция для корректного закрытия всех фоновых процессов при Ctrl+C
cleanup() {
    echo -e "\n[NeoMarket] Останавливаю все процессы..."
    kill $(jobs -p)
    exit
}
trap cleanup SIGINT

# Запускаем в фоне
poetry run python manage.py runserver &
poetry run celery -A config worker --loglevel=info --pool=threads &
poetry run celery -A config beat --loglevel=info &

echo "-----------------------------------------------------------------------"
echo "[УСПЕХ] Всё готово! Откройте сайт: http://127.0.0.1:8000"
echo "Для остановки проекта нажмите Ctrl + C"
echo "-----------------------------------------------------------------------"

wait
