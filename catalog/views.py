from django.shortcuts import render, get_object_or_404, redirect  # noqa: F401
from django.contrib import messages
from django.views import View

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
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
        # Принудительно связываем таблицы по SKU на уровне базы данных
         return Product.objects.all().prefetch_related('images').order_by("id")


# Логика для страницы каталога
class CatalogListView(ListView):
    model = Product
    context_object_name = "products"

    def get_queryset(self):
        # ИСПРАВЛЕНО: Добавлен prefetch_related для страницы каталога
        return Product.objects.all().prefetch_related('images').order_by("id")


# Логика для страницы описания товара
class ProductDetailView(DetailView):
    model = Product
    context_object_name = "product"

    def get_queryset(self):
        # ИСПРАВЛЕНО: Добавлен prefetch_related для детальной страницы товара
        return super().get_queryset().prefetch_related('images')


# Логика удаления товара
class ProductDeleteView(DeleteView):
    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy("catalog:catalog_list")


# Логика для добавления нового товара
class ProductCreateView(CreateView):
    model = Product
    context_object_name = "product"
    form_class = ProductForm

    # Куда перенаправить пользователя после успешного создания товара
    success_url = reverse_lazy("catalog:catalog_list")

    # Текст всплывающего уведомления
    success_message = "Новый товар успешно добавлен в каталог!"


# Логика для редактирования товара
class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    context_object_name = "product"
    success_url = reverse_lazy("catalog:catalog_list")
    success_message = "Товар успешно отредактирован!"

    # 1. Передаем формсет с картинками в контекст HTML-шаблона
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = ProductImageFormSet(
                self.request.POST, 
                self.request.FILES, 
                instance=self.object
            )
        else:
            context['image_formset'] = ProductImageFormSet(instance=self.object)
        return context

    # 2. Перехватываем сохранение: проверяем и текст, и все картинки сразу
    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        
        if form.is_valid() and image_formset.is_valid():
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()  # Здесь Django сам удалит те фото, где стоят чекбоксы "Стереть"
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

# Логика удаления только фотографии товара
class ProductDeleteImageView(View):
    def post(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        
        # ИСПРАВЛЕНО: Теперь класс умеет работать с новой моделью ProductImage, привязанной по SKU
        # Он берет и удаляет ПЕРВУЮ картинку из галереи товара
        first_image = product.images.first()
        if first_image:
            first_image.image.delete(save=False) # Физически стираем файл
            first_image.delete() # Удаляем запись из таблицы ProductImage
            messages.success(request, "Фотография товара успешно удалена!")
            
        return redirect("catalog:product_edit", pk=pk)


# Логика для контактов с формой обратной связи
class ContactsView(TemplateView):
    template_name = "catalog/contacts.html"

    def post(self, request, *args, **kwargs):
        # Получаем данные из полей формы
        name = request.POST.get("name")  # noqa: F841
        request.POST.get("phone")
        message = request.POST.get("message")  # noqa: F841

        # Создаем всплывающее уведомление об успехе
        messages.success(
            request,
            "Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.",
        )

        # Перенаправляем на ту же страницу контактов
        return redirect(request.path)
