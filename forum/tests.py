# Create your tests here.
from django.test import TestCase
from django.utils import timezone
from .models import Book
from datetime import datetime

class BookTestCase(TestCase):
    def setUp(self):
        Book.objects.create(title="Book 1", author="Author 1", publication_date=timezone.now())
        Book.objects.create(title="Book 2", author="Author 2", publication_date=timezone.now())

    def test_books_have_correct_titles(self):
        """Books have correct titles."""
        book1 = Book.objects.get(title="Book 1")
        book2 = Book.objects.get(title="Book 2")
        self.assertEqual(book1.title, "Book 1")
        self.assertEqual(book2.title, "Book 2")

    def test_books_have_correct_authors(self):
        """Books have correct authors."""
        book1 = Book.objects.get(title="Book 1")
        book2 = Book.objects.get(title="Book 2")
        self.assertEqual(book1.author, "Author 1")
        self.assertEqual(book2.author, "Author 2")

    def test_books_have_publication_dates_in_the_past(self):
        """Books have publication dates in the past."""
        today = datetime.today().date()  # Get today's date
        book1 = Book.objects.get(title="Book 1")
        book2 = Book.objects.get(title="Book 2")
        self.assertLessEqual(book1.publication_date, today)
        self.assertLessEqual(book2.publication_date, today)