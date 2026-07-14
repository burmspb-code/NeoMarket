from django.urls import path
from django.views.decorators.cache import cache_page

from catalog.apps import CatalogConfig
from catalog.views import (
    HomeListView,
    ContactsView,
    CatalogListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ProductDeleteImageView,
    CategoryProductsListView,
)

app_name = CatalogConfig.name

urlpatterns = [
    # Главная страница (Каталог)
    path("", HomeListView.as_view(), name="home"),
    # Страница контактов
    path(
        "contacts/", cache_page(60 * 60 * 24)(ContactsView.as_view()), name="contacts"
    ),
    # Страница с каталогом товаров
    path("catalog/", CatalogListView.as_view(), name="catalog_list"),
    # Страница с добавлением нового товара
    path("product/add/", ProductCreateView.as_view(), name="product_create"),
    # Страница с детальной информацией о товаре
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
    # Страница для редактирования товара
    path("product/<slug:slug>/edit/", ProductUpdateView.as_view(), name="product_edit"),
    # Станица для удаления товара
    path(
        "product/<slug:slug>/delete/",
        ProductDeleteView.as_view(),
        name="product_delete",
    ),
    # Станица для удаления фото товара
    path(
        "product/<slug:slug>/delete-image/",
        ProductDeleteImageView.as_view(),
        name="product_delete_image",
    ),
    # Страница товаров выбранной категории
    path(
        "category/<slug:slug>/",
        CategoryProductsListView.as_view(),
        name="category_products",
    ),
]
