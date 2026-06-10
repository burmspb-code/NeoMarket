from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.urls import reverse_lazy
from catalog.models import Product
from .forms import ProductForm


# Логика для главной страницы спагинацией
class HomeListView(ListView):
    model = Product
    template_name = "catalog/index.html"
    context_object_name = "products"
    paginate_by = 3

    def get_queryset(self):
        return Product.objects.all().order_by("id")


# Логика для страницы каталога
class CatalogListView(ListView):
    model = Product
    context_object_name = "products"



# Логика для страницы детального описания товара
class ProductDetailView(DetailView):
    model = Product
    context_object_name = "product"


# Логика для добавления нового товара
class ProductCreateView(CreateView):
    model = Product
    context_object_name = "product"
    form_class = ProductForm

    # Куда перенаправить пользователя после успешного создания товара
    success_url = reverse_lazy("catalog:catalog_list")

    # Текст всплывающего уведомления
    success_message = "Новый товар успешно добавлен в каталог!"


# Логика для контактов с формой обратной связи
class ContactsView(TemplateView):
    template_name = "catalog/contacts.html"

    def post(self, request, *args, **kwargs):
        # Получаем данные из полей формы
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        # Создаем всплывающее уведомление об успехе
        messages.success(
            request,
            "Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.",
        )

        # Перенаправляем на ту же страницу контактов, чтобы очистить форму (защита от дублирования F5)
        return redirect(request.path)
