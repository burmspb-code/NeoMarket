import os
import re

from django import forms
from django.core.exceptions import ValidationError
from django.db.models.fields.files import ImageFieldFile
from django.forms import inlineformset_factory

from .models import Category, Product, ProductImage

# Варианты для радиокнопки
PUBLISHED_CHOICES = [(True, "Да"), (False, "Нет")]


class CategoryForm(forms.ModelForm):
    """Форма для категорий."""

    class Meta:
        model = Category
        fields = "__all__"


class ProductForm(forms.ModelForm):
    """Форма для продуктов."""

    FORBIDDEN_WORDS = [
        "казино",
        "криптовалюта",
        "крипта",
        "биржа",
        "дешево",
        "бесплатно",
        "обман",
        "полиция",
        "радар",
    ]

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Выберите категорию",
    )

    class Meta:
        model = Product
        fields = ["name", "sku", "description", "category", "price", "published"]

        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Введите наименование товара"}
            ),
            "sku": forms.TextInput(attrs={"placeholder": "Введите артикул"}),
            "description": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Введите описание товара..."}
            ),
            "price": forms.NumberInput(attrs={"placeholder": "0.00"}),
            "published": forms.RadioSelect(choices=PUBLISHED_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        """Автоматически добавляем Bootstrap-классы ко всем полям."""
        # Принимаем пользователя из контроллера (View)
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # ПРОВЕРКА ПРАВ: Если пользователя нет или он НЕ модератор
        if self.user and not self.user.has_perm("catalog.can_unpublish_product"):
            # Скрываем поле из вёрстки, чтобы обычный юзер его не видел
            self.fields["published"].widget = forms.HiddenInput()

        for field_name, field in self.fields.items():
            if field_name == "category":
                field.widget.attrs.update({"class": "form-select"})
            elif field_name != "published":
                # Добавляем класс ко всем полям, КРОМЕ радиокнопок published
                field.widget.attrs.update({"class": "form-control"})

    def clean_name(self):
        """Валидация поля названия товара."""
        name = self.cleaned_data.get("name")
        self._validate_text(name)
        return name

    def clean_description(self):
        """Валидация поля описания товара."""
        description = self.cleaned_data.get("description")
        self._validate_text(description)
        return description

    def _validate_text(self, text):
        """Вспомогательный метод для проверки текста на запрещенные слова."""
        if text:
            words_in_text = set(re.findall(r"\b\w+-?\w*\b", text.lower()))
            for word in self.FORBIDDEN_WORDS:
                if word in words_in_text:
                    raise forms.ValidationError(
                        f"Использование слова {word} запрещено в целях безопасности."
                    )

    def clean_price(self):
        """Валидация цены продукта."""
        price = self.cleaned_data.get("price")
        if price is not None and price <= 0:
            raise forms.ValidationError("Некорректное значение цены на товар.")
        return price


class ProductImageForm(forms.ModelForm):
    """Форма для фото."""

    class Meta:
        model = ProductImage
        fields = ["image"]
        widgets = {
            "image": forms.FileInput(
                attrs={"class": "form-control", "accept": ".jpg,.jpeg,.png"}
            )
        }

    def clean_image(self):
        """Валидация размера и расширения для загружаемых изображений."""
        image = self.cleaned_data.get("image")

        if not image:
            return image

        # Безопасно достаем имя файла (убран опасный бесконечный цикл)
        file_name = getattr(image, "name", "")
        if isinstance(file_name, (tuple, list)) and file_name:
            file_name = file_name[0]

        # Приводим к строке и берем только базовое имя файла (убираем пути вроде photo/)
        file_name = os.path.basename(str(file_name))

        # Извлекаем расширение файла (теперь там гарантированно строка вроде '.jpg')
        ext = os.path.splitext(file_name)[1].lower()
        valid_extensions = [".jpg", ".jpeg", ".png"]

        if ext not in valid_extensions:
            raise ValidationError(
                "Допускаются только изображения с расширением JPG, JPEG или PNG."
            )

        # Проверяем размер и MIME-тип ТОЛЬКО для новых загружаемых файлов
        if hasattr(image, "file") and not isinstance(image, ImageFieldFile):
            # Проверка размера (5 МБ)
            max_size = 5 * 1024 * 1024
            if image.size > max_size:
                raise ValidationError("Размер нового файла не должен превышать 5 МБ.")

            # Проверка MIME-типа (безопасность)
            content_type = getattr(image, "content_type", "").lower()
            valid_mime_types = ["image/jpeg", "image/png", "image/jpg"]

            if content_type and content_type != "application/octet-stream":
                if content_type not in valid_mime_types:
                    raise ValidationError("Файл имеет некорректный формат изображения.")

        return image


# FormSet для работы с галереей изображений
ProductImageFormSet = inlineformset_factory(
    Product, ProductImage, form=ProductImageForm, extra=1, can_delete=True
)
