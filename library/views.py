from django.shortcuts import render, get_object_or_404
from .models import Book

from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView


class BooksListView(ListView):
    model = Book
    template_name = 'books_list.html'
    context_object_name = 'books'


class BookCreateView(CreateView):
    model = Book
    fields = '__all__'
    template_name = 'book_form.html'
    success_url = reverse_lazy('library:books_list')


class BookDetailView(DetailView):
    model = Book
    template_name = 'book_detail.html'
    context_object_name = 'book'


class BookUpdateViews(UpdateView):
    model = Book
    fields = '__all__'
    template_name = 'book_form.html'
    success_url = reverse_lazy('library:books_list')


class BookDeleteView(DeleteView):
    model = Book
    template_name = 'book_confirm_delete.html'
    success_url = reverse_lazy('library:books_list')

