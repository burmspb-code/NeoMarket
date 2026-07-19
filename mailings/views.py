"""Контроллеры для управления сервисом рассылок."""

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView
from django.views.generic import ListView

from mailings.forms import MailingManagementForm
from mailings.models import MailingLog, MailingClient, MailingManagement, MailingMessage
from .tasks import send_single_mailing_task  # Импортируем нашу таску


class ManualStartMailingView(PermissionRequiredMixin, View):
    """Класс-контроллер (CBV) для запуска рассылки."""

    # Контент-менеджер должен иметь право изменять рассылки
    permission_required = "mailings.change_mailingmanagement"
    raise_exception = True

    def get(self, request, *args, **kwargs):
        """Обработка GET-запроса при клике на кнопку запуска."""
        mailing_id = kwargs.get("mailing_id")

        # БЕЗОПАСНОСТЬ: Админ может запустить любую рассылку, контент-менеджер — только свою
        if request.user.is_superuser:
            mailing = get_object_or_404(MailingManagement, pk=mailing_id)
        else:
            mailing = get_object_or_404(
                MailingManagement, pk=mailing_id, owner=request.user
            )

        now = timezone.now()

        # --- Проверка временных рамок ---
        if not (mailing.start_time <= now <= mailing.end_time):
            messages.error(
                request,
                f"Ошибка запуска: Текущее время вне рамок актуальности рассылки "
                f"({mailing.start_time:%d.%m.%Y %H:%M} — {mailing.end_time:%d.%m.%Y %H:%M}).",
            )
            return redirect(request.META.get("HTTP_REFERER", "mailings:dashboard"))

        # Проверяем наличие получателей перед отправкой в очередь
        if not mailing.recipients.exists():
            messages.warning(
                request,
                f"У рассылки '{mailing.message.message_subject}' нет получателей.",
            )
            return redirect(request.META.get("HTTP_REFERER", "mailings:dashboard"))

        # Меняем статус на "Запущена" (launched)
        mailing.status = "launched"
        mailing.save(update_fields=["status"])

        # --- Отправка задачи в Celery (Redis) ---
        # Метод .delay() мгновенно закидывает ID рассылки в Redis и возвращает управление.
        # Цикл отправки писем будет выполняться в фоне, не подвешивая браузер менеджера.
        send_single_mailing_task.delay(mailing.pk)

        # Выводим сообщение о том, что процесс пошел в фоне
        messages.success(
            request,
            f"Рассылка «{mailing.message.message_subject}» успешно запущена в фоновом режиме. "
            f"Результаты отправки будут появляться в логах.",
        )
        return redirect(request.META.get("HTTP_REFERER", "mailings:dashboard"))


class MailingDashboardView(PermissionRequiredMixin, ListView):
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
    template_name = "mailings/dashboard.html"
    context_object_name = "mailings"
    ordering = ["-start_time"]

    # Строгое требование права: <имя_приложения>.<действие>_<имя_модели_в_нижнем_регистре>
    permission_required = "mailings.view_mailingmanagement"

    # Что делать, если у пользователя нет этого права:
    # True — выкинет ошибку 403 Forbidden, False — перенаправит на страницу логина
    raise_exception = True

    def get_queryset(self):
        """Жадно подгружаем сообщения и фильтруем по автору."""
        # Получаем базовый queryset с уже настроенной жадной загрузкой сообщений
        queryset = super().get_queryset().select_related("message")

        # Если это администратор, отдаем все рассылки (с подгруженными сообщениями)
        if self.request.user.is_superuser:
            return queryset

        # Если это контент-менеджер, отдаем только его рассылки
        return queryset.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        """Расчет показателей для карточек аналитики и выгрузка логов."""
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        # Количество кампаний (рассылок) в системе
        context["total_mailings"] = MailingManagement.objects.count()
        context["active_mailings"] = MailingManagement.objects.filter(
            status="launched", start_time__lte=now, end_time__gte=now
        ).count()
        context["total_clients"] = MailingClient.objects.count()

        # Считаем суммарное количество адресатов по ВСЕМ созданным рассылкам
        # Мы используем сквозной подсчет связей Many-to-Many
        context["total_emails_targeted"] = MailingManagement.objects.values(
            "recipients"
        ).count()

        # Универсальный подсчет логов (физически выполненные попытки отправки)
        successful_attempts = MailingLog.objects.filter(status="success").count()
        total_logs_in_db = MailingLog.objects.count()
        failed_attempts = total_logs_in_db - successful_attempts

        context["successful_attempts"] = successful_attempts
        context["failed_attempts"] = failed_attempts
        context["total_sent_messages"] = total_logs_in_db

        return context


class MailingCreateView(PermissionRequiredMixin, CreateView):
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
    template_name = "mailings/mailing_form.html"

    # Строгое требование права на создание рассылки
    permission_required = "mailings.add_mailingmanagement"
    raise_exception = True

    # Перенаправление обратно на дашборд после успешного создания
    success_url = reverse_lazy("mailings:dashboard")

    def form_valid(self, form):
        """Обрабатывает сценарий, когда отправленная форма валидна.

        Автоматически назначает текущего авторизованного пользователя автором
        рассылки и принудительно устанавливает статус 'created'.
        """
        # БЕЗОПАСНОСТЬ: Насильно привязываем текущего контент-менеджера к полю owner
        form.instance.owner = self.request.user

        # Извлекаем данные виртуальных полей
        subject = form.cleaned_data.get("message_subject")
        body = form.cleaned_data.get("message_body")

        # Если поля заполнены, создаем новый объект MailingMessage в базе
        if subject and body:
            new_message = MailingMessage.objects.create(
                message_subject=subject, message_body=body
            )
            # Привязываем новое сообщение к рассылке
            form.instance.message = new_message

        # Принудительно выставляем статус 'created' для рассылки
        form.instance.status = "created"

        return super().form_valid(form)


class MailingLogListView(PermissionRequiredMixin, ListView):
    """Страница для просмотра полной истории логов отправки писем."""

    model = MailingLog
    template_name = "mailings/log_list.html"
    context_object_name = "logs"
    paginate_by = 20  # Показываем по 20 логов на страницу

    # Требуем то же право, что и для просмотра дашборда
    permission_required = "mailings.view_mailingmanagement"
    raise_exception = True


class MailingDetailView(PermissionRequiredMixin, DetailView):
    """Контроллер для отображения детальной информации о рассылке и списка её получателей."""

    model = MailingManagement
    template_name = "mailings/mailing_detail.html"
    context_object_name = "mailing"
    permission_required = "mailings.view_mailingmanagement"
    raise_exception = True

    def get_context_data(self, **kwargs):
        """Сбор данных их БД для шаблона HTML."""
        # Сбор баозового словаря в переменную context
        context = super().get_context_data(**kwargs)
        # Добавляем новый ключ, обращаемся к полю recipients, описанному в модели
        context["clients"] = self.object.recipients.all()
        return context

    def get_object(self, queryset=None):
        """Возвращает объект рассылки из низкоуровневого кэша Redis."""
        # Получаем ID текущей рассылки из URL-параметров
        mailing_id = self.kwargs.get(self.pk_url_kwarg) or self.kwargs.get("pk")

        # Формируем уникальный динамический ключ кэша для этой рассылки
        cache_key = f"mailing_detail_{mailing_id}"

        # Пытаемся достать объект из Redis
        mailing_object = cache.get(cache_key)

        if not mailing_object:
            # Если в Redis пусто — делаем один тяжелый оптимизированный запрос в базу
            mailing_object = (
                MailingManagement.objects.select_related("message")
                .prefetch_related("recipients")
                .get(pk=mailing_id)
            )

            # Сохраняем объект в Redis на 10 минут (600 секунд)
            cache.set(cache_key, mailing_object, 600)
            print(
                f"[Django Cache] Запись с ID {mailing_id} не найдена в Redis. Загружено из БД и закэшировано."
            )
        else:
            print(
                f"[Django Cache] Успех! Запись с ID {mailing_id} мгновенно получена из Redis."
            )

        return mailing_object
