from django.test import TestCase # type: ignore

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from .models import Book, CustomUser

class BookModelTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            genre="Test Genre",
            status="available"
        )

    def test_book_creation(self):
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.author, "Test Author")
        self.assertEqual(self.book.genre, "Test Genre")
        self.assertEqual(self.book.status, "available")

class BookListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('book_list')

    def test_book_list_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_list.html')

class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpassword",
            role="admin"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertTrue(self.user.check_password("testpassword"))
        self.assertEqual(self.user.role, "admin")
