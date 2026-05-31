from django.urls import path
from library.apps import LibraryConfig
from library.views import books_list, book_detail

app_name = LibraryConfig.name

urlpatterns = [
    path("library_list/", books_list, name="books_list"),
    path("library_detail/<int:book_id>/", book_detail, name="book_detail"),
]
