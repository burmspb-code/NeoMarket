from django import forms
from django.forms import inlineformset_factory
from .models import Category, Product, ProductImage


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        # Добавили все поля в отображаемые
        fields = "__all__"


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Добавили все поля в отображаемые
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

# Фабрика, которая автоматически создаст чекбоксы DELETE для картинок товара
ProductImageFormSet = inlineformset_factory(
    Product, 
    ProductImage, 
    fields=['image'], 
    # Ставим строго 1 пустой слот при загрузке страницы
    extra=1, 
    can_delete=True
)