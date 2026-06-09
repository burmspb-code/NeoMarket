from django.urls import path
from library.apps import LibraryConfig
from library.views import BooksListView, BookDetailView, BookCreateView, BookUpdateView, BookDeleteView


app_name = LibraryConfig.name

urlpatterns = [
    path('books/', BooksListView.as_view(), name='books_list'),
    path('books/new/', BookCreateView.as_view(), name='book_new'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('books/update/<int:pk>/', BookUpdateView.as_view(), name='book_update'),
    path('books/delete/<int:pk>/', BookDeleteView.as_view(), name='book_delete'),
]
