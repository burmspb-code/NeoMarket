from django.urls import path
from library.apps import LibraryConfig
from library.views import (
    AuthorsListView,
    AuthorCreateView,
    AuthorUpdateView,
    BooksListView,
    BookDetailView,
    BookCreateView,
    BookUpdateView,
    BookDeleteView,
)


app_name = LibraryConfig.name

urlpatterns = [
    path("authors/", AuthorsListView.as_view(), name="authors_list"),
    path("author/new/", AuthorCreateView.as_view(), name="author_create"),
    path("author/update/<int:pk>/", AuthorUpdateView.as_view(), name="author_update"),
    path("books/", BooksListView.as_view(), name="books_list"),
    path("books/new/", BookCreateView.as_view(), name="book_new"),
    path("books/<int:pk>/", BookDetailView.as_view(), name="book_detail"),
    path("books/update/<int:pk>/", BookUpdateView.as_view(), name="book_update"),
    path("books/delete/<int:pk>/", BookDeleteView.as_view(), name="book_delete"),
]
