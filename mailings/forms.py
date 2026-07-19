from django import forms
from mailings.models import MailingManagement


class MailingManagementForm(forms.ModelForm):
    """Форма для создания и редактирования параметров рассылки.

    Обеспечивает ввод временных рамок кампании, множественный выбор получателей
    (клиентов интернет-магазина NeoMarket), а также альтернативные варианты работы
    с контентом: выбор готового шаблона из базы данных либо создание новой темы
    и текста письма прямо на лету в интерфейсе формы.

    Все поля автоматически стилизуются CSS-классами под компоненты фреймворка
    Bootstrap 5.

    Attributes:
        message_subject (CharField): Виртуальное (не связанное с моделью напрямую)
            поле для ввода темы нового сообщения при создании на лету.
        message_body (CharField): Виртуальное текстовое поле для ввода
            тела/содержимого нового сообщения при создании на лету.

    Args:
        *args: Позиционные аргументы, передаваемые в конструктор базовой формы.
        **kwargs: Именованные аргументы, передаваемые в конструктор базовой формы.
    """

    message_subject = forms.CharField(
        max_length=150,
        required=False,
        label="Тема нового сообщения",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Введите тему письма"}
        ),
    )
    message_body = forms.CharField(
        required=False,
        label="Текст нового сообщения",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Введите текст письма",
            }
        ),
    )

    class Meta:
        """Метаданные формы, определяющие связь с моделью Django и конфигурацию полей.

        Attributes:
            model (MailingManagement): Модель, на основе которой строится форма.
            fields (list[str]): Список полей модели, доступных для заполнения.
            widgets (dict): Словарь кастомных HTML-виджетов и атрибутов
                для адаптации полей под UI-шаблон.
        """

        model = MailingManagement
        fields = ["start_time", "end_time", "message", "recipients"]

        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "end_time": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "message": forms.Select(attrs={"class": "form-select"}),
            "recipients": forms.SelectMultiple(
                attrs={"class": "form-select", "size": "5"}
            ),
        }

    def __init__(self, *args, **kwargs):
        """Инициализирует экземпляр формы и настраивает выпадающий список сообщений."""
        super().__init__(*args, **kwargs)
        self.fields["message"].required = False
        self.fields["message"].label = "Выберите сообщение для рассылки"

        # Меняем дефолтные прочерки '---------' на понятный пункт для создания
        self.fields["message"].empty_label = "+ Создать новое сообщение"

    def clean(self):
        """Выполняет комплексную валидацию взаимосвязанных полей формы.

        Проверяет, обеспечена ли рассылка текстовым контентом. Менеджер обязан
        выбрать хотя бы один из двух путей: либо указать существующий шаблон
        в поле выбора, либо полностью заполнить тему и тело нового письма.
        В случае нарушения этого правила генерируется общая ошибка валидации.

        Raises:
            ValidationError: Если не выбран готовый шаблон и одновременно
                с этим отсутствует заполненная тема или текст нового письма.

        Returns:
            dict[str, Any]: Словарь очищенных и проверенных данных `cleaned_data`.
        """
        cleaned_data = super().clean()
        message = cleaned_data.get("message")
        subject = cleaned_data.get("message_subject")
        body = cleaned_data.get("message_body")

        # Валидация бизнес-логики: исключаем отправку пустых рассылок
        if not message and (not subject or not body):
            raise forms.ValidationError(
                "Необходимо либо выбрать готовый шаблон сообщения, "
                "либо заполнить тему и текст для нового письма."
            )

        return cleaned_data
