from django import forms  # type: ignore
from django.contrib.auth.forms import UserCreationForm  # type: ignore
from library.models import CustomUser  # type: ignore
from django.contrib.auth.forms import AuthenticationForm  # type: ignore
from .models import Book, BorrowedBook, Review


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'genre']
from .models import Book, BorrowedBook, Review

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'genre']
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        widgets = {
            'review_text': forms.Textarea(attrs={'rows': 4}),
        }

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role']



#class LoginForm(AuthenticationForm):
   
   # class Meta:
        #model = CustomUser  # Make AuthenticationForm work with CustomUser
        
        #fields = ['username', 'password']
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})        

class AdminCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

class RoleChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['role']

class RatingForm(forms.ModelForm):
    class Meta:
        model = BorrowedBook
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }
