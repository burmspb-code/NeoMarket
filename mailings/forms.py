from django import forms
from mailings.models import MailingManagement


class MailingManagementForm(forms.ModelForm):
    """Форма для создания и редактирования параметров рассылки.

        Обеспечивает ввод временных рамок кампании, выбор шаблона сообщения
        и множественный выбор получателей (клиентов интернет-магазина).
        Автоматически стилизует поля под элементы UI фреймворка Bootstrap 5.

        Attributes:
            Meta (class): Класс метаданных, определяющий связь с моделью
                MailingManagement и перечень редактируемых полей.
    """
    class Meta:
        """Класс метаданных."""
        model = MailingManagement
        # Поле status исключаем, так как при создании оно должно быть 'created' автоматически
        fields = ['start_time', 'end_time', 'message', 'recipients']

        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'end_time': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'message': forms.Select(attrs={'class': 'form-select'}),
            'recipients': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '6'}),
        }
