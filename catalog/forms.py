from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Добавили 'category' в список отображаемых полей
        fields = "__all__"

        # Настройка Bootstrap-стилей для всех полей формы
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите наименование товара",
                }
            ),
            "category": forms.Select(
                attrs={"class": "form-select"}
            ),  # Для ForeignKey используем выпадающий список Select
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Введите описание товара...",
                }
            ),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "0.00"}
            ),
        }

        # Переопределяем подписи (хотя они подтянутся из verbose_name модели, здесь их можно зафиксировать)
        labels = {
            "name": "Наименование товара",
            "category": "Категория",
            "description": "Описание",
            "image": "Фото товара",
            "price": "Стоимость (руб.)",
        }
