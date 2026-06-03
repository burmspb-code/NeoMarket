from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from catalog.models import Product
from django.core.paginator import Paginator  # Для прокрутки страниц
from .forms import ProductForm


# Логика для главной страницы спагинацией
def home_view(request):
    products_list = Product.objects.all().order_by(
        "id"
    )  # Сортировка обязательна для пагинации

    # Показывать по 3 товара на странице
    paginator = Paginator(products_list, 3)

    # Получаем номер текущей страницы из URL (например, /?page=2)
    page_number = request.GET.get("page")

    # Получаем товары конкретно для этой страницы
    page_obj = paginator.get_page(page_number)

    # Передаем page_obj в контекст под именем products
    context = {"products": page_obj}
    return render(request, "catalog/index.html", context)


# Логика для страницы каталога
def catalog_view(request):
    products = Product.objects.all()
    context = {"products": products}
    return render(request, "catalog/catalog_view.html", context)


# Логика для страницы детального описания товара
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "catalog/product_detail.html", {"product": product})


# Логика для добавления нового товара
def product_create_view(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Сохраняем в базу данных
            messages.success(request, "Новый товар успешно добавлен в каталог!")
            return redirect(
                "catalog:catalog_list"
            )  # Перенаправление на страницу каталога
    else:
        form = ProductForm()  # Пустая форма

    return render(request, "catalog/product_form.html", {"form": form})


# Логика для контактов с формой обратной связи
def contacts_view(request):
    if request.method == "POST":
        # Получаем данные из полей формы
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        # Создаем всплывающее уведомление об успехе
        messages.success(
            request,
            "Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.",
        )
    return render(request, "catalog/contacts.html")
