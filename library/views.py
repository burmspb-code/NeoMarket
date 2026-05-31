from django.shortcuts import render, get_object_or_404
from .models import Book


def books_list(request):
    books = Book.objects.all()
    context = {'books': books}
    return render(request, 'library/books_list.html', context)

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    context = {'book': book}
    return render(request, 'library/book_detail.html', context)
