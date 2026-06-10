from django.db import models


class Post(models.Model):
    title = models.CharField(
        max_length=150,
        verbose_name="Название",
        help_text="Введите название статьи",
    )
    content = models.TextField(
        verbose_name="Содержимое",
        help_text="Введите текст статьи"
    )
    preview  = models.ImageField(
        upload_to="blog_previews/",
        blank=True,
        null=True,
        verbose_name="Фото",
        help_text="Загрузите превью товара",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="Признак публикации",
        help_text="Снимите галочку, чтобы скрыть статью"
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Количество просмотров"
    )

    class Meta:
        verbose_name = "Блоговая запись"
        verbose_name_plural = "Блоговые записи"
        ordering = ["-created_at"] # Свежие статьи сверху

    def __str__(self):
            return self.title
