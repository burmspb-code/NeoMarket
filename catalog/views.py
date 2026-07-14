from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect  # noqa: F401
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)

from catalog.models import Product
from .forms import ProductForm, ProductImageFormSet
from catalog.services import get_products_cache


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
    """Представление для отображения каталога товаров.

        Использует встроенный класс `ListView` для вывода списка продуктов.
        Вся логика выборки, фильтрации и кэширования данных делегирована
        сервисному слою приложения.
    """
    model = Product
    context_object_name = "products"

    def get_queryset(self):
        """Возвращает оптимизированный и кэшированный список опубликованных товаров."""
        return get_products_cache()


# Логика для страницы описания товара
class ProductDetailView(DetailView):
    model = Product
    context_object_name = "product"

    def get_queryset(self):
        user = self.request.user
        # ИСПРАВЛЕНИЕ: Добавили "owner" в select_related, чтобы Django сразу знал создателя товара
        base_queryset = (
            super()
            .get_queryset()
            .prefetch_related("images")
            .select_related("category", "owner")
        )

        # Проверяем права БЕЗОПАСНО (работает и для гостей, и для авторизованных)
        if user.is_authenticated and user.has_perm("catalog.can_unpublish_product"):
            # Модераторы и админы видят абсолютно все товары (включая черновики)
            return base_queryset

        # Всем остальным (у кого нет этого права) показываем только опубликованные
        return base_queryset.filter(published=True)


# Логика удаления товара
class ProductDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Product
    context_object_name = "product"
    success_url = reverse_lazy("catalog:catalog_list")
    success_message = "Товар успешно снят с публикации и перенесен в архив!"

    def dispatch(self, request, *args, **kwargs):
        """Проверяем, имеет ли право пользователь архивировать этот товар."""
        product = self.get_object()
        user = request.user

        # Допуск получают только владелец товара или модератор/админ с правом delete_product
        if product.owner == user or user.has_perm("catalog.delete_product"):
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied("Вы можете архивировать только собственные товары.")

    def form_valid(self, form):
        """Переопределяем удаление: вместо DELETE делаем UPDATE флага published."""
        success_url = self.get_success_url()

        # Меняем статус публикации на False (отправляем в архив)
        self.object.published = False
        self.object.save()

        # Вызываем метод SuccessMessageMixin, чтобы зафиксировать сообщение об успехе
        if self.success_message:
            from django.contrib import messages

            messages.success(self.request, self.success_message)

        return HttpResponseRedirect(success_url)


# Логика для добавления нового товара
class ProductCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Product
    context_object_name = "product"
    form_class = ProductForm
    success_url = reverse_lazy("catalog:catalog_list")
    success_message = "Новый товар успешно добавлен в каталог!"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Передаем текущего пользователя в форму
        kwargs["user"] = self.request.user
        return kwargs

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
            # НАЗНАЧАЕМ ВЛАДЕЛЬЦА И СТАТУС ДО СОХРАНЕНИЯ
            form.instance.owner = self.request.user

            # Безопасность: если не модератор, товар улетает на модерацию (черновик)
            if not self.request.user.has_perm("catalog.can_unpublish_product"):
                form.instance.published = False

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
class ProductUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Product
    form_class = ProductForm
    context_object_name = "product"
    success_url = reverse_lazy("catalog:catalog_list")
    success_message = "Товар успешно отредактирован!"

    def dispatch(self, request, *args, **kwargs):
        """Гибкая проверка прав: пускаем модераторов ИЛИ владельца товара."""
        product = self.get_object()
        user = request.user

        # 1. Если пользователь — создатель товара (сравниваем ID для надежности)
        # 2. ИЛИ у пользователя есть глобальное право модератора change_product
        if product.owner.id == user.id or user.has_perm("catalog.change_product"):
            return super().dispatch(request, *args, **kwargs)

        # Во всех остальных случаях жестко возвращаем 403 ошибку
        raise PermissionDenied("Вы можете редактировать только собственные товары.")

    def get_queryset(self):
        """Оптимизируем запросы к базе данных."""
        return (
            super()
            .get_queryset()
            .prefetch_related("images")
            .select_related("category", "owner")
        )

    def get_form_kwargs(self):
        """Передаем текущего пользователя в форму, чтобы скрыть радиокнопки для продавцов."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

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
