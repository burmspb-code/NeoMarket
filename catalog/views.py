from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from catalog.models import Product


# Логика для главной страницы
def home_view(request):
    products = Product.objects.all()[:3] # Берем первые три товара
    context = {'products':products}
    return render(request, 'catalog/index.html', context)

# Логика для страницы каталога
def catalog_view(request):
    products = Product.objects.all()
    context = {'products':products}
    return render(request, "catalog/catalog_view.html", context)

# Логика для страницы детального описания товара
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "catalog/product_detail.html", {'product':product})

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