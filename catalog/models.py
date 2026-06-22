from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=150,
        verbose_name="Наименование",
        help_text="Введите наименование категории",
    )
    description = models.TextField(
        verbose_name="Описание", help_text="Введите описание категории"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"
        ordering = ["name"]


class Product(models.Model):
    name = models.CharField(
        max_length=150,
        verbose_name="Наименование",
        help_text="Введите наименование товара",
    )
    sku = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Артикул",
        help_text="Введите уникальный артикул товара (обязательно)",
    )
    description = models.TextField(
        verbose_name="Описание", help_text="Введите описание товара"
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

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"
        ordering = ["-created_at"]


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        to_field="sku",
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
