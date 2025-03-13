from django.contrib import admin # type: ignore
from .models import Book, CustomUser  # Import your models

# Register your models here.
admin.site.register(Book)
admin.site.register(CustomUser)
