#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys
import socket
import subprocess
from django.conf import settings


def start_local_redis():
    """Автоматически проверяет и запускает локальный Redis-сервер в фоне."""
    if not settings.CACHE_ENABLED:
        return

    if (
        os.environ.get("RUN_MAIN") == "true"
        and len(sys.argv) > 1
        and sys.argv[1] in ["runserver", "shell"]
    ):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        try:
            s.connect(("127.0.0.1", 6379))
            s.close()
            print("[Django Redis] Redis-сервер обнаружен и успешно подключен.")
        except socket.error:
            my_local_redis_path = r"C:\My_projects\Redis-x64-3.0.504\redis-server.exe"

            if os.path.exists(my_local_redis_path):
                print("[Django Autostart] Локальный Redis выключен. Запускаю в фоне...")
                subprocess.Popen(
                    [my_local_redis_path], creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
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
        raise ImportError("Couldn't import Django...") from exc

    start_local_redis()  # Оставляем только автоматический запуск Redis

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
