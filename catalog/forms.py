from django import forms
from django.forms import inlineformset_factory
from .models import Category, Product, ProductImage


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        # Добавили все поля в отображаемые
        fields = "__all__"


class ProductForm(forms.ModelForm):
    # Переопределяем поле для категории
    category = forms.ModelChoiceField(
    queryset=Category.objects.all(),
    empty_label="Выберите категорию",
    widget=forms.Select(attrs={'class': 'form-select'})  # Переносим стиль виджета сюда
    )

    class Meta:
        model = Product
        # Добавили поля в отображаемые
        fields = ['name', 'sku', 'description', 'category', 'price']

        # Настройка Bootstrap-стилей для всех полей формы
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите наименование товара",
                }
            ),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите артикул'}),
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
            "description": "Описание",
            "image": "Фото товара",
            "price": "Стоимость (руб.)",
        }

# Автоматическое создание чекбоксов для картинок товара
ProductImageFormSet = inlineformset_factory(
    Product, 
    ProductImage, 
    fields=['image'], 
    # Ставим 1 пустой слот при загрузке страницы
    extra=1, 
    can_delete=True
)