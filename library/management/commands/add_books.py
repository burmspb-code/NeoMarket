from django.core.management import BaseCommand
from library.models import Author, Book


class Command(BaseCommand):
    help = "Add books to the database"

    def handle(self, *args, **options):
        author, _ = Author.objects.get_or_create(
            first_name="Антон", last_name="Чехов", birth_date="1869-01-29"
        )

        books = [
            {
                "title": "Вишневый сад",
                "publication_date": "1904-01-01",
                "author": author,
            },
            {"title": "Три сестры", "publication_date": "1901-01-01", "author": author},
        ]

        for book_data in books:
            book, create = Book.objects.get_or_create(**book_data)

            if create:
                self.stdout.write(
                    self.style.SUCCESS(f"Successfulle added book: {book.title}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Book already exist: {book.title}")
                )
