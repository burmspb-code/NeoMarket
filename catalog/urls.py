from django.urls import path
from catalog.views import home_view, contacts_view

app_name = "catalog"

urlpatterns = [
    # Главная страница (Каталог)
    path("", home_view, name="home"),
    # Страница контактов
    path("contacts/", contacts_view, name="contacts"),
]
