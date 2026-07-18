"""Контроллеры для управления сервисом рассылок."""

import smtplib

from django.contrib import messages
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView
from django.views.generic import ListView

from mailings.forms import MailingManagementForm
from mailings.models import MailingLog, MailingClient, MailingManagement, MailingMessage


class ManualStartMailingView(View):
    """Класс-контроллер (CBV) для ручного запуска рассылки через веб-интерфейс."""

    def get(self, request, *args, **kwargs):
        """Обработка GET-запроса при клике на кнопку запуска."""
        # Получаем ID рассылки из именованных аргументов URL
        mailing_id = kwargs.get('mailing_id')
        mailing = get_object_or_404(MailingManagement, pk=mailing_id)
        now = timezone.now()

        # --- Проверка временных рамок ---
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

        # --- Отправка писем и логирование ---
        for client in recipients:
            # Берем имя или подставляем заглушку, если поле пустое
            client_name = client.full_name if client.full_name else "Розничный клиент"

            try:
                send_mail(
                    subject=mailing.message.message_subject,
                    message=mailing.message.message_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                # Записываем в строку ответа ФИО и Email получателя писем
                MailingLog.objects.create(
                    mailing=mailing,
                    status='success',
                    server_response=f"Адресат: {client_name} | Email: {client.email} | Статус: Доставлено (200 OK)"
                )
                success_count += 1
            except (smtplib.SMTPException, Exception) as e:
                # Записываем детальные данные сбоя для конкретного человека
                MailingLog.objects.create(
                    mailing=mailing,
                    status='failed',
                    server_response=f"Адресат: {client_name} | Email: {client.email} | Ошибка SMTP: {str(e)}"
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


class MailingDashboardView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Класс-контроллер (CBV) для отображения панели мониторинга (Дашборда) рассылок.

    Выводит ключевые метрики эффективности маркетинговых кампаний NeoMarket
    (общее число рассылок, количество активных в текущую секунду процессов
    и общий объем базы клиентов) совместно со списком всех запланированных
    и завершенных рассылок.

    Доступ разрешен только пользователям с правом 'mailings.view_mailingmanagement'.

    Attributes:
        model (Model): Модель управления рассылками (MailingManagement).
        template_name (str): Путь к HTML-шаблону страницы дашборда.
        context_object_name (str): Имя переменной списка рассылок в шаблоне.
        ordering (list): Критерий сортировки записей (новые рассылки сверху).
        permission_required (str): Системное право для просмотра дашборда.
        raise_exception (bool): Флаг генерации ошибки 403 при нехватке прав.
    """
    model = MailingManagement
    template_name = 'mailings/dashboard.html'
    context_object_name = 'mailings'
    ordering = ['-start_time']

    # Строгое требование права: <имя_приложения>.<действие>_<имя_модели_в_нижнем_регистре>
    permission_required = 'mailings.view_mailingmanagement'

    # Что делать, если у пользователя нет этого права:
    # True — выкинет ошибку 403 Forbidden, False — перенаправит на страницу логина
    raise_exception = True

    def get_queryset(self):
        """Жадно подгружаем сообщения для исключения пустых строк в шаблоне."""
        return super().get_queryset().select_related('message')

    def get_context_data(self, **kwargs):
        """Расчет показателей для карточек аналитики и выгрузка логов."""
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        # Количество кампаний (рассылок) в системе
        context['total_mailings'] = MailingManagement.objects.count()
        context['active_mailings'] = MailingManagement.objects.filter(
            status='launched',
            start_time__lte=now,
            end_time__gte=now
        ).count()
        context['total_clients'] = MailingClient.objects.count()

        # Считаем суммарное количество адресатов по ВСЕМ созданным рассылкам
        # Мы используем сквозной подсчет связей Many-to-Many
        context['total_emails_targeted'] = MailingManagement.objects.values('recipients').count()

        # Универсальный подсчет логов (физически выполненные попытки отправки)
        successful_attempts = MailingLog.objects.filter(status='success').count()
        total_logs_in_db = MailingLog.objects.count()
        failed_attempts = total_logs_in_db - successful_attempts

        context['successful_attempts'] = successful_attempts
        context['failed_attempts'] = failed_attempts
        context['total_sent_messages'] = total_logs_in_db

        return context


class MailingCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Класс-контроллер (CBV) для создания новой кампании рассылки.

    Предоставляет менеджеру интерфейс для планирования рассылки. Доступ к странице
    строго ограничен на уровне групп и прав доступа Django (требуется системное
    разрешение 'mailings.add_mailingmanagement').

    При успешной валидации формы автоматически переопределяет статус рассылки
    на 'created' (Создана) перед сохранением записи в базу данных.

    Attributes:
        model (Model): Модель управления рассылками (MailingManagement).
        form_class (ModelForm): Класс используемой формы (MailingManagementForm).
        template_name (str): Путь к HTML-шаблону страницы формы.
        permission_required (str): Системное право, необходимое для доступа.
        raise_exception (bool): Флаг вызова ошибки 403 Forbidden при отказе в доступе.
        success_url (str): URL-адрес для перенаправления после успешного создания.
    """
    model = MailingManagement
    form_class = MailingManagementForm
    template_name = 'mailings/mailing_form.html'

    # Строгое требование права на создание рассылки
    permission_required = 'mailings.add_mailingmanagement'
    raise_exception = True

    # Перенаправление обратно на дашборд после успешного создания
    success_url = reverse_lazy('mailings:dashboard')

    def form_valid(self, form):
        """Обрабатывает сценарий, когда отправленная форма валидна.

        Принудительно устанавливает статус рассылки в значение 'created'
        для обеспечения корректного жизненного цикла кампании в системе.

        Args:
            form (MailingManagementForm): Экземпляр валидированной формы.

        Returns:
            HttpResponse: Перенаправление на страницу success_url.
        """
        # Извлекаем данные виртуальных полей
        subject = form.cleaned_data.get('message_subject')
        body = form.cleaned_data.get('message_body')

        # Если поля заполнены, создаем новый объект MailingMessage в базе
        if subject and body:
            new_message = MailingMessage.objects.create(
                message_subject=subject,
                message_body=body
            )
            # Привязываем новое сообщение к рассылке
            form.instance.message = new_message

        # Принудительно выставляем статус 'created' для рассылки
        form.instance.status = 'created'
        return super().form_valid(form)


class MailingLogListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Страница для просмотра полной истории логов отправки писем."""
    model = MailingLog
    template_name = 'mailings/log_list.html'
    context_object_name = 'logs'
    paginate_by = 20  # Показываем по 20 логов на страницу

    # Требуем то же право, что и для просмотра дашборда
    permission_required = 'mailings.view_mailingmanagement'
    raise_exception = True


class MailingDetailView(PermissionRequiredMixin, DetailView):
    """Контроллер для отображения детальной информации о рассылке и списка её получателей."""
    model = MailingManagement
    template_name = 'mailings/mailing_detail.html'
    context_object_name = 'mailing'
    permission_required = 'mailings.view_mailingmanagement'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Исправлено: обращаемся к полю recipients, описанному в модели
        context['clients'] = self.object.recipients.all()
        return context
