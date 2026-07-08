from django.shortcuts import render, get_object_or_404, redirect  # noqa: F401
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)
from django.urls import reverse_lazy
from catalog.models import Product
from .forms import ProductForm, ProductImageFormSet


# Логика для главной страницы с пагинацией
class HomeListView(ListView):
    model = Product
    template_name = "catalog/index.html"
    context_object_name = "products"
    paginate_by = 3

    def get_queryset(self):
        # Фильтруем только опубликованные товары
        # Оптимизируем запросы: категории (SQL JOIN) и картинки (отдельный быстрый запрос)
        # Сортируем (для пагинации обязательна стабильная сортировка, "id" отлично подходит)
        return (
            Product.objects.filter(published=True)
            .select_related("category")
            .prefetch_related("images")
            .order_by("id")
        )

# Логика для страницы каталога
class CatalogListView(ListView):
    model = Product
    context_object_name = "products"

    def get_queryset(self):
        return (
            Product.objects.filter(published=True)
            .select_related("category")
            .prefetch_related("images")
            .order_by("id")
        )

# Логика для страницы описания товара
class ProductDetailView(DetailView):
    model = Product
    context_object_name = "product"

    def get_queryset(self):
        user = self.request.user
        # Базовый оптимизированный запрос
        base_queryset = super().get_queryset().prefetch_related("images").select_related("category")

        # Проверяем права БЕЗОПАСНО (работает и для гостей, и для авторизованных)
        # Метод has_perm вернет False для анонимного пользователя без ошибок
        if user.is_authenticated and user.has_perm('catalog.can_unpublish_product'):
            # Модераторы и админы видят абсолютно все товары (включая черновики)
            return base_queryset

        # Всем остальным (у кого нет этого права) показываем только опубликованные
        return base_queryset.filter(published=True)


# Логика удаления товара
class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy("catalog:catalog_list")


# Логика для добавления нового товара
class ProductCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Product
    context_object_name = "product"
    form_class = ProductForm
    success_url = reverse_lazy("catalog:catalog_list")
    success_message = "Новый товар успешно добавлен в каталог!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = ProductImageFormSet(
                self.request.POST, self.request.FILES
            )
        else:
            context["image_formset"] = ProductImageFormSet()
        return context

    def form_valid(self, form):
        # Получаем контекст, где уже лежит заполненный POST-данными формсет
        context = self.get_context_data()
        image_formset = context["image_formset"]

        # Проверяем ТОЛЬКО формсет, так как основная форма уже валидна
        if image_formset.is_valid():
            # Сначала сохраняем продукт (Django под капотом сделает self.object = form.save())
            response = super().form_valid(form)

            # Привязываем сохраненный продукт к формсету изображений
            image_formset.instance = self.object
            image_formset.save()

            return response
        else:
            # Если формсет невалиден, вызываем стандартный метод form_invalid.
            # Он автоматически вернет страницу с ошибками формы и формсета.
            return self.form_invalid(form)


# Логика для редактирования товара
class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Product
    form_class = ProductForm
    context_object_name = "product"
    success_url = reverse_lazy("catalog:catalog_list")
    success_message = "Товар успешно отредактирован!"

    # Указываем системное право Django на изменение, которое мы выдали модераторам в миграции
    permission_required = "catalog.change_product"

    def get_queryset(self):
        # Так как PermissionRequiredMixin уже отсек всех пользователей без прав,
        # здесь будут находиться ТОЛЬКО модераторы и администраторы.
        # Поэтому мы просто возвращаем весь оптимизированный запрос без лишних фильтров.
        return super().get_queryset().prefetch_related("images").select_related("category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = ProductImageFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            context["image_formset"] = ProductImageFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context["image_formset"]

        if form.is_valid() and image_formset.is_valid():
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            # Вызываем родительский метод, чтобы SuccessMessageMixin зафиксировал сообщение
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class ProductDeleteImageView(LoginRequiredMixin, View):
    def post(self, request, image_pk, *args, **kwargs):
        # Ищем конкретную картинку, попутно проверяя, существует ли она
        image_instance = get_object_or_404(ProductImage, pk=image_pk)

        # Запоминаем ID товара, чтобы после удаления вернуться на страницу его редактирования
        product_pk = image_instance.product.id

        # Физически удаляем файл с диска/облака
        if image_instance.image:
            image_instance.image.delete(save=False)

        # Удаляем запись из базы данных
        image_instance.delete()

        messages.success(request, "Фотография товара успешно удалена!")

        # Перенаправляем обратно в редактирование этого товара
        return redirect("catalog:product_edit", pk=product_pk)


# Логика для контактов с формой обратной связи
class ContactsView(TemplateView):
    template_name = "catalog/contacts.html"

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")  # noqa: F841
        request.POST.get("phone")
        message = request.POST.get("message")  # noqa: F841

        messages.success(
            request,
            "Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.",
        )
        return redirect(request.path)
