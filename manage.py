#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys
import subprocess


def start_local_redis():
    # Запускаем Redis только если мы пишем 'runserver' или заходим в 'shell'
    if len(sys.argv) > 1 and sys.argv[1] in ["runserver", "shell"]:
        # Проверяем, запущен ли уже Redis, чтобы не плодить процессы
        # Ошибка 10061 означает, что порт свободен, значит Redis выключен
        import socket

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(("127.0.0.1", 6379))
            s.close()
            # Если подключился — Redis уже работает, ничего делать не надо
        except socket.error:
            # Если порт закрыт — запускаем его скрытно в фоне
            # ЗАМЕНИТЕ ПУТЬ НИЖЕ НА ВАШ РЕАЛЬНЫЙ ПУТЬ К REDIS-SERVER.EXE
            redis_path = r"C:\My_projects\Redis-x64-3.0.504\redis-server.exe"

            if os.path.exists(redis_path):
                print("[Django Autostart] Локальный Redis выключен. Запускаю в фоне...")
                # Флаг CREATE_NO_WINDOW прячет черное окно навсегда!
                subprocess.Popen(
                    [redis_path], creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                print(
                    f"[Django Autostart] Предупреждение: Не найден redis-server.exe по пути {redis_path}"
                )


def main():
    """Run administrative tasks."""
    start_local_redis()  # Запуск Redis
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
