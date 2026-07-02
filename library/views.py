from .models import Author, Book
from .forms import AuthorForm, BookForm

from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin


class AuthorsListView(ListView):
    model = Author
    template_name = "library/authors_list.html"
    context_object_name = "authors"


class AuthorCreateView(LoginRequiredMixin, CreateView):
    model = Author
    form_class = AuthorForm
    template_name = "library/author_form.html"
    success_url = reverse_lazy("library:authors_list")


class AuthorUpdateView(LoginRequiredMixin, UpdateView):
    model = Author
    form_class = AuthorForm
    template_name = "libary/author_form.html"
    success_url = reverse_lazy("library:authors_list")


class BooksListView(ListView):
    model = Book
    template_name = "library/books_list.html"
    context_object_name = "books"


class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = "library/book_form.html"
    success_url = reverse_lazy("library:books_list")


class BookDetailView(DetailView):
    model = Book
    template_name = "library/book_detail.html"
    context_object_name = "book"


class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = "library/book_form.html"
    success_url = reverse_lazy("library:books_list")


class BookDeleteView(LoginRequiredMixin, DeleteView):
    model = Book
    template_name = "library/book_confirm_delete.html"
    success_url = reverse_lazy("library:books_list")
