"""Описание моделей приложения."""

from django.db import models
from django.conf import settings
from pytils.translit import slugify  # Импортируем «правильный» транслитератор


class Category(models.Model):
    """Модель категории для группировки товаров.
    Поля:
        name (CharField): Название категории, уникальное в пределах длины.
        slug (SlugField): Человекопонятный уникальный URL-адрес товара для карточки (SEO-ЧПУ).
        description (TextField): Подробное описание категории товаров.
    """

    name = models.CharField(
        max_length=150,
        verbose_name="Наименование",
        help_text="Введите наименование категории",
    )
    # Поле slug. unique=True обязательно для SEO и поиска.
    # blank=True позволяет оставлять поле пустым в админке (оно заполнится само).
    slug = models.SlugField(
        max_length=170, unique=True, blank=True, verbose_name="URL-слаг"
    )
    description = models.TextField(
        verbose_name="Описание", help_text="Введите описание категории"
    )

    class Meta:
        verbose_name = "категорию"
        verbose_name_plural = "категории"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Переопределение метода сохранения."""
        if not self.slug:
            # Из «Умные часы & гаджеты» сделает «umnye-chasy-i-gadzhety»
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Возвращает прямой URL-адрес страницы товаров данной категории."""
        from django.urls import reverse

        return reverse("catalog:category_products", kwargs={"slug": self.slug})


class Product(models.Model):
    """Модель товара, содержащая основные характеристики и связь с категорией.
    Поля:
        name (CharField): Наименование торговой позиции.
        slug (SlugField): Человекопонятный уникальный URL-адрес товара для карточки (SEO-ЧПУ).
        sku (CharField): Уникальный артикул товара для складского учета.
        description (TextField): Подробное описание характеристик товара.
        category (ForeignKey): Ссылка на категорию, к которой относится товар.
        price (DecimalField): Стоимость товара с точностью до двух знаков.
        created_at (DateTimeField): Дата и время автоматического добавления товара.
        updated_at (DateTimeField): Дата и время автоматического обновления товара.
        owner (ForeignKey): Ссылка на владельца, который создал данный товар.
        published (BooleanField): Признак публикации товара на сайте.
    """

    name = models.CharField(
        max_length=150,
        verbose_name="Наименование",
        help_text="Введите наименование товара",
    )
    slug = models.SlugField(
        max_length=170, unique=True, blank=True, verbose_name="URL-слаг товара"
    )
    sku = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Артикул",
        help_text="Введите уникальный артикул товара (обязательно)",
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text="Введите описание товара",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Категория",
        help_text="Выберите категорию товара",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Стоимость",
        help_text="Введите стоимость товара",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Подключение кастомной модели пользователя
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Владелец",
    )
    published = models.BooleanField(
        default=False,
        db_index=True,  # ставим индекс (значительно увеличивает скорость поиска на больших данных)
        verbose_name="Опубликован",
    )

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"
        ordering = ["-created_at"]
        permissions = [
            ("can_unpublish_product", "Может скрывать продукт"),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Переопределение метода сохранения."""
        if not self.slug:
            # Базовая генерация слага из названия
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            # Боевая проверка на уникальность: если такой slug уже есть,
            # добавляем цифру в конец (например, smartfon-iphone-15-1)
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class ProductImage(models.Model):
    """Модель для хранения изображений товара в рамках галереи.
    Поля:
        product (ForeignKey): Связь с моделью Product через уникальный артикул SKU.
        image (ImageField): Файл изображения товара, загружаемый в медиа-директорию.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",  # Через это имя мы будем выводить список фото
        verbose_name="Товар",
    )
    image = models.ImageField(upload_to="photo/", verbose_name="Фото")

    class Meta:
        verbose_name = "Фотография товара"
        verbose_name_plural = "Галерея товара"

    def __str__(self):
        return f"Фото для товара SKU: {self.product_id}"
