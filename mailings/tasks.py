import smtplib
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.db import transaction

from .models import MailingManagement, MailingLog


@shared_task
@transaction.atomic  # Открывает изолированный коридор транзакции
def send_single_mailing_task(mailing_id):
    """Фоновая задача Celery для поклиентной отправки конкретной рассылки."""
    try:
        # Блокируем строку в базе данных от параллельных потоков Celery
        mailing = MailingManagement.objects.select_for_update().select_related('message').prefetch_related(
            'recipients').get(pk=mailing_id)
    except MailingManagement.DoesNotExist:
        return f"Рассылка с ID {mailing_id} не найдена в базе данных."

    # ЗАЩИТА: Если рассылка уже была успешно обработана другим потоком — выходим
    if mailing.status == 'completed':
        print(f"[Celery Защита] Перехват дубликата! Рассылка {mailing_id} уже была отправлена.")
        return f"Рассылка {mailing_id} уже обработана другим потоком."

    recipients = mailing.recipients.all()
    if not recipients.exists():
        mailing.status = 'completed'
        mailing.save(update_fields=['status'])
        return f"Рассылка {mailing_id} отменена: нет получателей."

    success_count = 0
    failed_count = 0

    # --- ТОТ САМЫЙ КРАСИВЫЙ ПОКЛИЕНТНЫЙ ЦИКЛ ---
    for client in recipients:
        if not client.email:
            continue

        # Берем имя или подставляем заглушку, если поле пустое
        client_name = client.full_name if hasattr(client, 'full_name') and client.full_name else "Розничный клиент"

        try:
            # Отправляем письмо ЛИЧНО этому клиенту
            send_mail(
                subject=mailing.message.message_subject,
                message=mailing.message.message_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client.email],  # Строго один email в списке
                fail_silently=False,
            )

            # Логируем УСПЕХ для этого конкретного человека
            MailingLog.objects.create(
                mailing=mailing,
                status='success',
                server_response=f"Адресат: {client_name} | Email: {client.email} | Статус: Доставлено (200 OK)"
            )
            success_count += 1

        except (smtplib.SMTPException, Exception) as error:
            # Логируем СБОЙ только для этого конкретного человека (остальные письма уйдут!)
            MailingLog.objects.create(
                mailing=mailing,
                status='failed',
                server_response=f"Адресат: {client_name} | Email: {client.email} | Ошибка SMTP: {str(error)}"
            )
            failed_count += 1

    # После завершения цикла по всем клиентам официально закрываем кампанию
    mailing.status = 'completed'
    mailing.save(update_fields=['status'])

    return f"Рассылка {mailing_id} полностью обработана. Успешно: {success_count}, Сбоев: {failed_count}."


@shared_task
def check_and_run_mailings():
    """Периодическая задача (Робот): ежеминутно ищет кампании, которым пора стартовать."""
    now = timezone.now()

    # Поиск рассылок, у которых наступило время старта, не вышло время окончания и статус 'created'
    pending_mailings = MailingManagement.objects.filter(
        start_time__lte=now,
        end_time__gte=now,
        status='created'
    )

    for mailing in pending_mailings:
        # Переводим в статус 'launched' на уровне БД, чтобы исключить повторный запуск
        MailingManagement.objects.filter(pk=mailing.pk).update(status='launched')
        # Передаем задачу воркеру
        send_single_mailing_task.delay(mailing.pk)

    # Автоматическое завершение рассылок, у которых закончилось время жизни
    expired_mailings = MailingManagement.objects.filter(
        end_time__lt=now,
        status__in=['created', 'launched']
    )
    expired_mailings.update(status='completed')
