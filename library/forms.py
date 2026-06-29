from django import forms
from .models import Author, Book


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = [
            "first_name",
            "last_name",
            "birth_date",
        ]


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            "title",
            "publication_date",
            "author",
        ]
