"""Контроллеры для управления сервисом рассылок."""

import smtplib

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView
from django.views.generic import ListView

from mailings.forms import MailingManagementForm
from mailings.models import MailingLog, MailingClient
from mailings.models import MailingManagement


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

    def get_context_data(self, **kwargs):
        """Расчет показателей для карточек на фронтенде."""
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        context['total_mailings'] = MailingManagement.objects.count()
        context['active_mailings'] = MailingManagement.objects.filter(
            status='launched',
            start_time__lte=now,
            end_time__gte=now
        ).count()
        context['total_clients'] = MailingClient.objects.count()

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
        form.instance.status = 'created'
        return super().form_valid(form)
