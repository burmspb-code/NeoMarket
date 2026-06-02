from django.urls import path
from catalog.apps import CatalogConfig
from catalog.views import home_view, contacts_view, catalog_view, product_detail, product_create_view

app_name = CatalogConfig.name

urlpatterns = [
    # Главная страница (Каталог)
    path("", home_view, name="home"),
    # Страница контактов
    path("contacts/", contacts_view, name="contacts"),
    # Страница с каталогом товаров
    path("catalog/", catalog_view, name="catalog_list"),
    # Страница с детальной информацией о товаре
    path("product/<int:pk>/", product_detail, name="product_detail"),
    # Страница с добавлением нового товара
    path("product/add/", product_create_view, name="product_create"),
]
