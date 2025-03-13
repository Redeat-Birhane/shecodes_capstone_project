# library/models.py

from django.contrib.auth.models import AbstractUser # type: ignore
from django.db import models # type: ignore
from django.contrib.auth import get_user_model # type: ignore

from library_management_system import settings # type: ignore

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
        ('super_admin', 'Super Admin'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='student')
 

    def __str__(self):
        return self.username
    
class Book(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('borrowed', 'Borrowed')
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=[('available', 'Available'), ('borrowed', 'Borrowed')], default='available')
    def get_average_rating(self):
        # Calculate the average rating for the book
        reviews = self.reviews.all()
        if reviews:
            return reviews.aggregate(Avg('rating'))['rating__avg'] # type: ignore
        return None

    def __str__(self):
        return self.title
class Review(models.Model):
    book = models.ForeignKey(Book, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)  # type: ignore # Use get_user_model() for custom user model
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])  # Rating between 1 and 5
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review of {self.book.title} by {self.user.username}"
    
   

# Assuming you already have a CustomUser model and Book model
class BorrowedBook(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.book.title} borrowed by {self.user.username}"

    def is_overdue(self):
        return self.returned_at is None and self.due_date < timezone.now()




