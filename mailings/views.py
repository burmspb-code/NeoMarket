"""Контроллеры для управления сервисом рассылок."""

import smtplib
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View  # <-- Импортируем базовый класс View
from django.core.mail import send_mail
from mailings.models import MailingLog, MailingManagement


class ManualStartMailingView(View):
    """Класс-контроллер (CBV) для ручного запуска рассылки через веб-интерфейс."""

    def get(self, request, *args, **kwargs):
        """Обработка GET-запроса при клике на кнопку запуска."""
        # Получаем ID рассылки из именованных аргументов URL
        mailing_id = kwargs.get('mailing_id')
        mailing = get_object_or_404(MailingManagement, pk=mailing_id)
        now = timezone.now()

        # --- Пункт 4 ТЗ: Проверка временных рамок ---
        if not (mailing.start_time <= now <= mailing.end_time):
            messages.error(
                request,
                f"Ошибка запуска: Текущее время вне рамок актуальности рассылки "
                f"({mailing.start_time:%d.%m.%Y %H:%M} — {mailing.end_time:%d.%m.%Y %H:%M})."
            )
            return redirect(request.META.get('HTTP_REFERER', '/admin/'))

        # Находим получателей
        recipients = mailing.recipients.all()
        if not recipients.exists():
            messages.warning(request, f"У рассылки '{mailing.message.message_subject}' нет получателей.")
            return redirect(request.META.get('HTTP_REFERER', '/admin/'))

        # Меняем статус на "Запущена" (launched)
        mailing.status = 'launched'
        mailing.save(update_fields=['status'])

        success_count = 0
        failed_count = 0

        # --- Пункт 4 и 5 ТЗ: Отправка писем и логирование ---
        for client in recipients:
            try:
                send_mail(
                    subject=mailing.message.message_subject,
                    message=mailing.message.message_body,
                    from_email=None,
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                MailingLog.objects.create(
                    mailing=mailing,
                    status='success',
                    server_response='Письмо успешно доставлено через веб-интерфейс (CBV).'
                )
                success_count += 1
            except (smtplib.SMTPException, Exception) as e:
                MailingLog.objects.create(
                    mailing=mailing,
                    status='failed',
                    server_response=str(e)
                )
                failed_count += 1

        # Завершаем кампанию рассылки
        mailing.status = 'completed'
        mailing.save(update_fields=['status'])

        # Выводим отчет на экран пользователю
        messages.success(
            request,
            f"Рассылка полностью обработана. Успешно отправлено: {success_count}. "
            f"Ошибок доставки: {failed_count}."
        )
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
