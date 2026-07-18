"""Скрипт автоматического фонового запуска и отправки рассылок."""

import smtplib

from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from mailings.models import MailingManagement, MailingLog


class Command(BaseCommand):
    """Кастомная команда Django для автоматической обработки рассылок в фоне.

    Скрипт находит все актуальные рассылки, осуществляет техническую отправку
    писем через SMTP, фиксирует результаты в MailingLog и обновляет статусы.
    """

    help = "Запуск фонового процесса отправки активных рассылок"

    def handle(self, *args, **options):
        """Основной метод выполнения консольной команды."""
        now = timezone.now()
        self.stdout.write(self.style.MIGRATE_LABEL(f"[{now:%d.%m.%Y %H:%M:%S}] Запуск робота рассылок..."))

        # 1. Автоматически переводим рассылки, чье время истекло, в статус completed
        expired_mailings = MailingManagement.objects.filter(
            status__in=['created', 'launched'],
            end_time__lt=now
        )
        for mailing in expired_mailings:
            mailing.status = 'completed'
            mailing.save(update_fields=['status'])
            self.stdout.write(self.style.WARNING(f"Рассылка ID {mailing.id} завершена по времени."))

        # 2. Находим рассылки, которые должны работать прямо сейчас
        # Статус 'created' (но время уже пришло) или 'launched' (уже в процессе)
        active_mailings = MailingManagement.objects.filter(
            status__in=['created', 'launched'],
            start_time__lte=now,
            end_time__gte=now
        )

        if not active_mailings.exists():
            self.stdout.write(self.style.SUCCESS("Нет активных рассылок для отправки."))
            return

        for mailing in active_mailings:
            # Если рассылка только стартовала, меняем статус на launched
            if mailing.status == 'created':
                mailing.status = 'launched'
                mailing.save(update_fields=['status'])

            recipients = mailing.recipients.all()
            if not recipients.exists():
                self.stdout.write(self.style.WARNING(f"У рассылки ID {mailing.id} нет получателей. Пропускаем."))
                continue

            self.stdout.write(
                f"Обработка рассылки '{mailing.message.message_subject}' для {recipients.count()} клиентов...")

            # 3. Отправка писем получателям
            for client in recipients:
                # Опционально: здесь можно добавить проверку в MailingLog,
                # чтобы не отправлять одному и тому же клиенту письмо повторно,
                # если скрипт запускается каждые 5 минут, а рассылка долгосрочная.

                # Формируем имя или ставим заглушку, если оно не заполнено
                client_name = client.full_name if getattr(client, 'full_name', None) else "Розничный клиент"

                try:
                    send_mail(
                        subject=mailing.message.message_subject,
                        message=mailing.message.message_body,
                        from_email=None,  # Берется из DEFAULT_FROM_EMAIL в settings.py
                        recipient_list=[client.email],
                        fail_silently=False,
                    )
                    # ИСПРАВЛЕНО: Пишем в лог персональный отчет об успешной доставке
                    MailingLog.objects.create(
                        mailing=mailing,
                        status='success',
                        server_response=f"Получатель: {client_name} | Email: {client.email} | Статус: Доставлено фоновым роботом"
                    )
                except (smtplib.SMTPException, Exception) as e:
                    # ИСПРАВЛЕНО: Пишем точечный отчет о сбое для конкретного адресата
                    MailingLog.objects.create(
                        mailing=mailing,
                        status='failed',
                        server_response=f"Получатель: {client_name} | Email: {client.email} | Сбой SMTP: {str(e)}"
                    )

            self.stdout.write(self.style.SUCCESS(f"Рассылка ID {mailing.id} успешно обработана."))
