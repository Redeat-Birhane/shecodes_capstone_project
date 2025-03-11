from datetime import timedelta
from django.contrib import messages  # type: ignore # Correct import
from django.shortcuts import render, redirect  # type: ignore
from django.contrib.auth import login, authenticate  # type: ignore
from .decorators import role_required
from django.utils import timezone # type: ignore
from django.shortcuts import get_object_or_404  # type: ignore
from .models import CustomUser, Review
from .forms import LoginForm, ReviewForm  # Ensure you are using the correct form
from django.contrib.auth.decorators import login_required, user_passes_test  # type: ignore
from .models import Book
from .forms import BookForm
from .forms import RegisterForm  # type: ignore
from django.contrib.auth.forms import AuthenticationForm  # type: ignore # Make sure this is added
from django.views.decorators.csrf import csrf_exempt # type: ignore
from .models import Book, BorrowedBook
from django.conf import settings # type: ignore
from django.http import HttpResponse # type: ignore
from django.shortcuts import get_object_or_404 # type: ignore

def return_book(request, borrowed_book_id):
    # Ensure the user is logged in
    if not request.user.is_authenticated:
        return redirect('login')

    borrowed_book = get_object_or_404(BorrowedBook, id=borrowed_book_id)

    # Check if the logged-in user is the one who borrowed this book
    if borrowed_book.user != request.user:
        return HttpResponse("You can't return a book you didn't borrow.", status=403)

    # Update the borrowed book's returned date
    borrowed_book.returned_at = timezone.now()
    borrowed_book.save()

    # Update the book's status to available (optional)
    borrowed_book.book.status = 'available'
    borrowed_book.book.save()

    return redirect('book_list')  # Redirect back to the book list or a return success page
def borrow_book(request, book_id):
    # Ensure the user is logged in
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login page if not authenticated

    user = request.user
    book = Book.objects.get(id=book_id)

    # Check if user has already borrowed 3 books
    borrowed_books_count = BorrowedBook.objects.filter(user=user, returned_at__isnull=True).count()
    if borrowed_books_count >= 3:
        return HttpResponse("You can only borrow a maximum of 3 books at a time.", status=400)

    # Check if the book is already borrowed (it doesn't have a returned date)
    if BorrowedBook.objects.filter(book=book, returned_at__isnull=True).exists():
        return HttpResponse("This book is already borrowed by someone else.", status=400)

    # Calculate due date (e.g., 14 days from now)
    due_date = timezone.now() + timedelta(days=14)

    # Create a BorrowedBook entry
    BorrowedBook.objects.create(
        user=user,
        book=book,
        due_date=due_date
    )

    # Update book status if needed (optional, if you want to mark it as borrowed)
    book.status = 'borrowed'
    book.save()

    return redirect('book_list')  # Redirect to the book list page

def home(request):
    return render(request, 'home.html')  # Ensure you have a template 'home.html'

@login_required
@user_passes_test(lambda user: user.role == 'super_admin')


# views.py


@login_required
def book_list(request):
    books = Book.objects.all()
    return render(request, 'books/book_list.html', {'books': books})

@csrf_exempt  # This disables CSRF protection for this view
def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Redirect based on role
            if user.is_superuser:
                return redirect('super_admin_dashboard')
            elif user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            messages.error(request, "Invalid login credentials. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})




def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)  # Use custom login form
        if form.is_valid():
            user = form.get_user()  # Get the user from the form
            login(request, user)  # Log the user in
            return redirect('home')  # Redirect to home page after successful login
    else:
        form = LoginForm()  # Instantiate the login form if GET request

    return render(request, 'login.html')  # Render login page with form

@login_required
@user_passes_test(lambda user: user.role == 'super_admin')
def ban_student(request, student_id):
    student = get_object_or_404(CustomUser, id=student_id)
    if student.role == 'student':
        student.is_active = False
        student.save()
        messages.success(request, f"Student {student.username} has been banned.")
    else:
        messages.error(request, "Only students can be banned.")
    
    return redirect('manage_users')

# views.py


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user
            user.role = form.cleaned_data['role']  # Save the selected role
            user.save()  # Don't forget to save the user after assigning the role

            # Log the user in after registration
            login(request, user)
            messages.success(request, "Registration successful! You are now logged in.")
            
            # Redirect based on the user's role
            if user.role == 'superadmin':
                return redirect('super_admin_dashboard')
            elif user.role == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            messages.error(request, "Error in registration. Please try again.")
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


@role_required(allowed_roles=['admin', 'super_admin'])
def manage_books(request):
    # code to manage books
    return render(request, 'manage_books.html')

@role_required(allowed_roles=['super_admin'])
def manage_users(request):
    users = CustomUser.objects.all()  # or filter users based on certain conditions
    return render(request, 'manage_users.html', {'users': users})

@role_required(allowed_roles=['super_admin'])
def change_role(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        new_role = request.POST['role']
        user.role = new_role
        user.save()
        return redirect('manage_users')
    return render(request, 'change_role.html', {'user': user})

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

def is_superadmin(user):
    return user.is_authenticated and user.role == 'superadmin'

@login_required
@user_passes_test(lambda user: user.role == 'student')
def view_books(request):
    books = Book.objects.all()
    return render(request, 'view_books.html', {'books': books})

@login_required
def role_based_redirect(request):
    user = request.user
    if user.role == 'admin':
        return redirect('manage_books')  # Redirect to admin dashboard or book management
    else:
        return redirect('student_dashboard')  # Redirect to student dashboard (borrow books, etc.)
    
@login_required
def manage_books(request):
    # This view is for admins and super admins
    if request.user.role in ['admin', 'super_admin']:
        books = Book.objects.all()
        return render(request, 'manage_books.html', {'books': books})
    return redirect('home')  # Redirect non-admins to the home page

@login_required
def superadmin_dashboard(request):
    return render(request, 'superadmin_dashboard.html')  # Superadmin page

# Admin dashboard (e.g., Manage Books)
@login_required
def manage_books(request):
    return render(request, 'manage_books.html')  # Admin page for managing books

# Student dashboard
@login_required
def student_dashboard(request):
    return render(request, 'student_dashboard.html')  # Student page

def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
def list_books(request):
    books = Book.objects.all()
    return render(request, 'books/list_books.html', {'books': books})

@user_passes_test(is_admin)
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form})

@user_passes_test(is_admin)
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form})

@user_passes_test(is_superadmin)
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})


def view_users(request):
    return render(request, 'view_users.html')  # Ensure this template exists

@login_required
def submit_review(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # Check if the user has already submitted a review for this book
    if Review.objects.filter(user=request.user, book=book).exists():
        # If already reviewed, you can either prevent or allow updating the review
        return redirect('book_detail', book_id=book.id)  # Redirect to the book detail page

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Create the review instance
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            return redirect('book_detail', book_id=book.id)
    else:
        form = ReviewForm()

    return render(request, 'submit_review.html', {'form': form, 'book': book})



def book_list(request):
    # Get search query from GET parameters
    search_query = request.GET.get('search', '')
    genre_filter = request.GET.get('genre', '')
    author_filter = request.GET.get('author', '')
    status_filter = request.GET.get('status', '')

    # Filter books based on search and other filters
    books = Book.objects.all()

    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |  # Filter by title
            Q(author__icontains=search_query) |  # Filter by author
            Q(genre__icontains=search_query)     # Filter by genre
        )

    if genre_filter:
        books = books.filter(genre__icontains=genre_filter)

    if author_filter:
        books = books.filter(author__icontains=author_filter)

    if status_filter:
        books = books.filter(status__icontains=status_filter)

    return render(request, 'book_list.html', {
        'books': books,
        'search_query': search_query,
        'genre_filter': genre_filter,
        'author_filter': author_filter,
        'status_filter': status_filter,
    })


