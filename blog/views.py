from django.contrib.messages.views import SuccessMessageMixin
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
        return obj
    

# Создание статьи
class PostCreateView(SuccessMessageMixin, CreateView):
    model = Post
    fields = ["title", "content", "preview", "is_published"]
    template_name = "blog/post_form.html"
    success_url = reverse_lazy("blog:list")
    success_message = "Статья «%(title)s» успешно создана!"


# Редактирование статьи
class PostUpdateView(SuccessMessageMixin, UpdateView):
    model = Post
    fields = ["title", "content", "preview", "is_published"]
    template_name = "blog/post_form.html"

    def get_success_url(self):
        return reverse_lazy("blog:detail", kwargs={"pk": self.object.pk})


# Удаление статьи
class PostDeleteView(DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("blog:list")

