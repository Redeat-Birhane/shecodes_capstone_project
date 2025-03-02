from django.db import models # type: ignore

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    publication_date = models.DateField()
    genre = models.CharField(max_length=100)
    available = models.BooleanField(default=True)

    def str(self):
        return self.title
