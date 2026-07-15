from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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

from catalog.models import Product, Category
from catalog.services import get_products_cache, get_products_by_category_cache
from .forms import ProductForm, ProductImageFormSet


# Логика для главной страницы с пагинацией
class HomeListView(ListView):
    """Представление для главной страницы сайта.
    Выводит опубликованные товары из кэша Redis с ручной пагинацией списка.
    """

    model = Product
    template_name = "catalog/index.html"
    context_object_name = "products"

    # Отключаем встроенную пагинацию, так как мы сделаем её вручную для списка
    paginate_by = None
    queryset = Product.objects.none()

    def get_context_data(self, **kwargs):
        """Передаем закешированный список товаров из сервисного слоя в контекст."""
        context = super().get_context_data(**kwargs)

        # Получаем ПОЛНЫЙ список товаров из Redis
        products_list = get_products_cache()

        # Получаем номер текущей страницы из URL-адреса (?page=2)
        page_number = self.request.GET.get("page", 1)

        # Вручную создаем пагинатор Django по 3 товара на страницу
        # Для изменения лимита просто поменяйте цифру 3 ниже
        paginator = Paginator(products_list, 3)

        try:
            # Пытаемся получить товары для текущей страницы
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            # Если page не число (например, ?page=abc), отдаем первую страницу
            page_obj = paginator.page(1)
        except EmptyPage:
            # Если страница пустая (например, ?page=999), отдаем последнюю страницу
            page_obj = paginator.page(paginator.num_pages)

        # Наполняем контекст переменными, которые ЖЕСТКО требуются HTML-шаблону
        context.update(
            {
                "paginator": paginator,
                "page_obj": page_obj,
                "is_paginated": paginator.num_pages
                > 1,  # Пагинация включена, если страниц больше 1
                "products": page_obj.object_list,  # Сюда уйдут ровно 3 товара для текущей страницы
            }
        )
        return context


# Логика для страницы каталога
class CatalogListView(ListView):
    """Представление для отображения каталога товаров.

    Использует встроенный класс `ListView` для вывода списка продуктов.
    Вся логика выборки, фильтрации и кэширования данных делегирована
    сервисному слою приложения.
    """

    model = Product
    context_object_name = "products"

    # Обязательно указываем путь к вашему HTML-шаблону
    template_name = "catalog/catalog_list.html"

    # Передаем пустой QuerySet, чтобы успокоить внутренние проверки Django
    queryset = Product.objects.none()

    def get_context_data(self, **kwargs):
        """Передаем готовый список из Redis прямо в контекст шаблона."""
        context = super().get_context_data(**kwargs)

        # Заменяем пустой список на наш быстрый кэш из сервисного слоя
        context["products"] = get_products_cache()

        return context


# Логика для страницы описания товара
class ProductDetailView(DetailView):
    """Представления для отображения детального описания товара."""
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
    """Представление для удаления товара."""
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
    """Представление для создания товара."""
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
    """Представление для редавтирования товара."""
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
    """Представления для удаления изображения товара."""
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
    """Представления для отображения формы обратной связи."""
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


class CategoryProductsListView(ListView):
    """Представление для отображения продуктов конкретной категории.

    Делегирует получение отфильтрованного списка товаров сервисному слою
    с низкоуровневым кэшированием в Redis на основе текстовых слагов.
    """

    model = Product
    template_name = "catalog/category_products.html"
    context_object_name = "products"

    # Заглушаем требование к QuerySet, так как данные придут в виде списка из Redis
    queryset = Product.objects.none()

    def get_context_data(self, **kwargs):
        """Дополняет контекст шаблона закешированными товарами и объектом категории."""
        context = super().get_context_data(**kwargs)

        # Извлекаем из URL текстовый 'slug' вместо числового 'pk'
        category_slug = self.kwargs.get("slug")

        # Передаем список товаров из сервисного слоя напрямую в контекст
        context["products"] = get_products_by_category_cache(category_slug)

        # ОПТИМИЗАЦИЯ: Получаем сам объект категории для вывода заголовка и описания
        # Чтобы не дергать БД при каждом клике, объект категории тоже можно закешировать
        category_cache_key = f"category_obj_{category_slug}"
        category = cache.get(category_cache_key)

        if category is None:
            category = Category.objects.filter(slug=category_slug).first()
            if category:
                cache.set(category_cache_key, category, timeout=3600)  # Кэш на 1 час

        context["category"] = category
        return context
