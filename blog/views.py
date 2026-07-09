from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .models import Post


# Список всех опубликованных статей
class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        # Показываем только опубликованные посты
        return Post.objects.filter(is_published=True).order_by("-created_at")


# Детальный просмотр статьи + счетчик просмотров
class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save()

        # Строгое условие на 100 просмотров
        if obj.views_count == 100:
            send_mail(
                subject="Поздравляем! Статья набрала 100 просмотров",
                message=f"Ваша статья «{obj.title}» успешно достигла отметки в 100 просмотров!",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.EMAIL_ADMIN_NOTIFICATION],
                fail_silently=True,  # Ошибка отправки не сломает загрузку страницы читателю
            )

        return obj


# Создание статьи
class PostCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Post
    fields = ["title", "content", "preview", "is_published"]
    template_name = "blog/post_form.html"
    success_message = "Статья «%(title)s» успешно создана!"

    def get_form(self, form_class=None):
        """Исключаем поле ОПУБЛИКОВАНО, если нет прав."""
        form = super().get_form(form_class)
        if not self.request.user.has_perm("blog.change_post"):
            del form.fields["is_published"]
        return form

    def form_valid(self, form):
        """Перехватываем сохранение формы, чтобы автоматически назначить автора."""
        # Назначаем полю owner текущего авторизованного пользователя
        form.instance.owner = self.request.user

        # Если поля нет в форме (у обычного автора), принудительно ставим False (черновик)
        if "is_published" not in form.fields:
            form.instance.is_published = False

        # Вызываем родительский метод, который теперь успешно сохранит запись без IntegrityError
        return super().form_valid(form)

    def get_success_url(self):
        # Перекидывает автора на детальный просмотр только что созданной статьи
        # self.object — это только что созданная и сохраненная статья
        return reverse_lazy("blog:detail", kwargs={"pk": self.object.pk})


# Редактирование статьи
class PostUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Post
    fields = ["title", "content", "preview", "is_published"]
    template_name = "blog/post_form.html"
    success_message = (
        "Статья успешно обновлена!"  # Текст сообщения для SuccessMessageMixin
    )

    def dispatch(self, request, *args, **kwargs):
        """Гибкая проверка прав: пускаем модераторов ИЛИ владельца статьи."""
        self.object = self.get_object()
        user = request.user

        # 1. Если пользователь — создатель товара (сравниваем ID для надежности)
        # 2. ИЛИ у пользователя есть глобальное право модератора change_product
        if self.object.owner == user or user.has_perm("blog.change_post"):
            return super().dispatch(request, *args, **kwargs)

        # Во всех остальных случаях жестко возвращаем 403 ошибку
        raise PermissionDenied("Вы можете редактировать только собственные статьи.")

    def get_form(self, form_class=None):
        """Исключаем поле ОПУБЛИКОВАНО, если нет прав."""
        form = super().get_form(form_class)
        if not self.request.user.has_perm("blog.change_post"):
            del form.fields["is_published"]
        return form

    def get_success_url(self):
        return reverse_lazy("blog:detail", kwargs={"pk": self.object.pk})


# Удаление статьи
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("blog:list")
    success_message = "Статья успешно снята с публикации и перенесена в архив!"

    def dispatch(self, request, *args, **kwargs):
        """Гибкая проверка прав: пускаем модераторов ИЛИ владельца статьи."""
        self.object = self.get_object()
        user = request.user

        # 1. Если пользователь — создатель товара (сравниваем ID для надежности)
        # 2. ИЛИ у пользователя есть глобальное право модератора change_product
        if self.object.owner == user or user.has_perm("blog.change_post"):
            return super().dispatch(request, *args, **kwargs)

        # Во всех остальных случаях жестко возвращаем 403 ошибку
        raise PermissionDenied(
            "Вы можете отправлять в архив только собственные статьи."
        )

    def form_valid(self, form):
        """Переопределяем удаление: вместо DELETE делаем UPDATE флага is_published."""
        success_url = self.get_success_url()

        # Меняем статус публикации на False (отправляем в архив)
        self.object.is_published = False
        self.object.save()

        # Вызываем метод SuccessMessageMixin, чтобы зафиксировать сообщение об успехе
        if self.success_message:
            messages.success(self.request, self.success_message)

        return HttpResponseRedirect(success_url)
