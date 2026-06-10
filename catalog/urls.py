from django.urls import path
from catalog.apps import CatalogConfig
from catalog.views import (
    HomeListView,
    ContactsView,
    CatalogListView,
    ProductDetailView,
    ProductCreateView,
)

app_name = CatalogConfig.name

urlpatterns = [
    # Главная страница (Каталог)
    path("", HomeListView.as_view(), name="home"),
    # Страница контактов
    path("contacts/", ContactsView.as_view(), name="contacts"),
    # Страница с каталогом товаров
    path("catalog/", CatalogListView.as_view(), name="catalog_list"),
    # Страница с детальной информацией о товаре
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    # Страница с добавлением нового товара
    path("product/add/", ProductCreateView.as_view(), name="product_create"),
]
