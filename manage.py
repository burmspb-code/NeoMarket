#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys
import socket
import subprocess
from django.conf import settings  # Импортируем настройки Django


def start_local_redis():
    """Автоматически проверяет и запускает локальный Redis-сервер в фоне.

    Логика работы:
    1. Проверяет флаг `CACHE_ENABLED` в настройках Django. Если он выключен, работа прекращается.
    2. Гарантирует выполнение только в основном процессе Django (игнорирует Autoreloader).
    3. Опрашивает порт 6379. Если порт занят — использует уже активный Redis.
    4. Если порт свободен и это мой ПК (путь к .exe существует) — запускает скрытый фоновый процесс.
    5. Если порт свободен, но пути к .exe нет (чужой ПК) — выводит предупреждение в консоль.
    """

    # Проверяем переменную кеширования напрямую через объект settings
    if not settings.CACHE_ENABLED:
        return  # Если кэш выключен — останавливаем запуск

    # Запускаем проверку только при старте сервера или шелла
    # RUN_MAIN гарантирует, что код выполнится только один раз в основном процессе
    if (
        os.environ.get("RUN_MAIN") == "true"
        and len(sys.argv) > 1
        and sys.argv[1] in ["runserver", "shell"]
    ):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)  # Задаем таймаут, чтобы проверка не зависала
        try:
            s.connect(("127.0.0.1", 6379))
            s.close()
            # ПОРТ ЗАНЯТ: Redis уже работает
            print("[Django Redis] Redis-сервер обнаружен и успешно подключен.")
        except socket.error:
            # ПОРТ СВОБОДЕН: Redis выключен. Проверяем, чей это компьютер
            # Моя локальная директория
            my_local_redis_path = r"C:\My_projects\Redis-x64-3.0.504\redis-server.exe"

            if os.path.exists(my_local_redis_path):
                print("[Django Autostart] Локальный Redis выключен. Запускаю в фоне...")
                subprocess.Popen(
                    [my_local_redis_path], creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                # Это чужой компьютер  — просто вежливо предупреждаем
                print("\n" + "=" * 80)
                print(
                    "[DJANGO WARNING] Для работы кэширования страниц требуется запущенный Redis!"
                )
                print(
                    "Пожалуйста, запустите Redis-сервер локально на стандартном порту 6379."
                )
                print("=" * 80 + "\n")


def main():
    """Run administrative tasks."""

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    start_local_redis()  # Запуск Redis

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
