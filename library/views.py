from datetime import timedelta
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import CustomUser, Book, BorrowedBook, Review
from django.contrib.auth.forms import AuthenticationForm
from .forms import LoginForm, RatingForm, ReviewForm, AdminCreationForm, BookForm, RegisterForm, RoleChangeForm
from .decorators import role_required


@login_required
@role_required(allowed_roles=['admin', 'super_admin'])
def view_users(request):
    users = CustomUser.objects.all()
    return render(request, 'view_users.html', {'users': users})


@login_required
@role_required(allowed_roles=['admin', 'super_admin'])
def list_books_admin(request):
    books = Book.objects.all()
    return render(request, 'books/list_books_admin.html', {'books': books})

@login_required
@role_required(allowed_roles=['student'])
def list_books_student(request):
    books = Book.objects.all()
    return render(request, 'books/list_books_student.html', {'books': books})

@login_required
@role_required(allowed_roles=['student'])
def student_borrowed_books(request):
    user = request.user
    borrowed_books = BorrowedBook.objects.filter(user=user, returned_at__isnull=True)

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            borrowed_book_id = request.POST.get('borrowed_book_id')
            borrowed_book = get_object_or_404(BorrowedBook, id=borrowed_book_id)
            borrowed_book.rating = form.cleaned_data['rating']
            borrowed_book.save()
            return redirect('student_borrowed_books')

    return render(request, 'books/student_borrowed_books.html', {'borrowed_books': borrowed_books, 'form': RatingForm()})

@login_required
def return_book(request, borrowed_book_id):
    borrowed_book = get_object_or_404(BorrowedBook, id=borrowed_book_id)

    # Check if the logged-in user is the one who borrowed this book
    if borrowed_book.user != request.user:
        return HttpResponse("You can't return a book you didn't borrow.", status=403)

    # Update the borrowed book's returned date
    borrowed_book.returned_at = timezone.now()
    borrowed_book.save()

    # Update the book's status to available
    borrowed_book.book.status = 'available'
    borrowed_book.book.save()

    return redirect('student_borrowed_books')  # Redirect to the student's borrowed books page

@login_required
def borrow_book(request, book_id):
    user = request.user
    book = get_object_or_404(Book, id=book_id)

    # Check if the book is already borrowed
    if book.status == 'borrowed':
        return HttpResponse("This book is already borrowed by someone else.", status=400)

    # Check if the user has already borrowed 3 books
    borrowed_books_count = BorrowedBook.objects.filter(user=user, returned_at__isnull=True).count()
    if borrowed_books_count >= 3:
        return HttpResponse("You can only borrow a maximum of 3 books at a time.", status=400)

    # Calculate due date (e.g., 14 days from now)
    due_date = timezone.now() + timedelta(days=14)

    # Create a BorrowedBook entry
    BorrowedBook.objects.create(
        user=user,
        book=book,
        due_date=due_date
    )

    # Update book status to borrowed
    book.status = 'borrowed'
    book.save()

    return redirect('list_books_student')  # Redirect to the student book list page


@login_required
@user_passes_test(lambda user: user.role == 'admin')
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book added successfully.')
            return redirect('list_books')
        else:
            messages.error(request, 'Error adding book. Please try again.')
    else:
        form = BookForm()
    return render(request, 'books/add_book.html', {'form': form})



@login_required
@user_passes_test(lambda user: user.role == 'admin')
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('list_books')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/edit_book.html', {'form': form, 'book': book})


@login_required
@user_passes_test(lambda user: user.role == 'admin')
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    messages.success(request, 'Book deleted successfully.')
    return redirect('list_books')


@login_required
def list_books(request):
    books = Book.objects.all()
    return render(request, 'books/list_books.html', {'books': books})

@csrf_exempt
def custom_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Redirect based on role
            if user.role == 'super_admin':
                return redirect('superadmin_dashboard')
            elif user.role == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            messages.error(request, "Invalid login credentials. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

@login_required
@role_required(allowed_roles=['super_admin'])
def superadmin_dashboard(request):
    return render(request, 'superadmin_dashboard.html')

@login_required
@role_required(allowed_roles=['admin'])
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
@role_required(allowed_roles=['student'])
def student_dashboard(request):
    return render(request, 'student_dashboard.html')

@login_required
@role_required(allowed_roles=['super_admin'])
def manage_admins(request):
    admins = CustomUser.objects.filter(role='admin')
    if request.method == 'POST':
        form = AdminCreationForm(request.POST)
        if form.is_valid():
            admin = form.save(commit=False)
            admin.role = 'admin'
            admin.save()
            messages.success(request, 'Admin created successfully.')
            return redirect('manage_admins')
    else:
        form = AdminCreationForm()
    return render(request, 'manage_admin.html', {'admins': admins, 'form': form})

@login_required
@role_required(allowed_roles=['super_admin'])
def delete_admin(request, admin_id):
    admin = get_object_or_404(CustomUser, id=admin_id, role='admin')
    admin.delete()
    messages.success(request, 'Admin deleted successfully.')
    return redirect('manage_admins')

@login_required
@role_required(allowed_roles=['super_admin'])
def manage_superadmins(request):
    superadmins = CustomUser.objects.filter(role='super_admin')
    if request.method == 'POST':
        form = AdminCreationForm(request.POST)
        if form.is_valid():
            superadmin = form.save(commit=False)
            superadmin.role = 'super_admin'
            superadmin.save()
            messages.success(request, 'Super Admin created successfully.')
            return redirect('manage_superadmins')
    else:
        form = AdminCreationForm()
    return render(request, 'manage_superadmin.html', {'superadmins': superadmins, 'form': form})

@login_required
@role_required(allowed_roles=['super_admin'])
def delete_superadmin(request, superadmin_id):
    superadmin = get_object_or_404(CustomUser, id=superadmin_id, role='super_admin')
    superadmin.delete()
    messages.success(request, 'Super Admin deleted successfully.')
    return redirect('manage_superadmins')

def home(request):
    return render(request, 'home.html')


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
    return redirect('view_users')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.role = form.cleaned_data['role']
            user.save()

            login(request, user)
            messages.success(request, "Registration successful! You are now logged in.")
            
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

@login_required
@role_required(allowed_roles=['admin', 'super_admin'])
def manage_books(request):
    books = Book.objects.all()
    return render(request, 'books/manage_books.html', {'books': books})

@role_required(allowed_roles=['super_admin'])
def manage_users(request):
    users = CustomUser.objects.all()
    return render(request, 'manage_users.html', {'users': users})

@login_required
@role_required(allowed_roles=['super_admin'])
def create_admin(request):
    if request.method == 'POST':
        form = AdminCreationForm(request.POST)
        if form.is_valid():
            admin = form.save(commit=False)
            admin.role = 'admin'
            admin.save()
            messages.success(request, 'Admin created successfully.')
            return redirect('superadmin_dashboard')
    else:
        form = AdminCreationForm()
    return render(request, 'create_admin.html', {'form': form})

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
        return redirect('manage_books')
    else:
        return redirect('student_dashboard')

@login_required
@role_required(allowed_roles=['super_admin'])
def change_role(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = RoleChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Role for {user.username} has been changed.")
            return redirect('manage_users')
    else:
        form = RoleChangeForm(instance=user)
    return render(request, 'change_role.html', {'form': form, 'user': user})

@login_required
def submit_review(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if Review.objects.filter(user=request.user, book=book).exists():
        return redirect('book_detail', book_id=book.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            return redirect('book_detail', book_id=book.id)
    else:
        form = ReviewForm()

    return render(request, 'submit_review.html', {'form': form, 'book': book})

def book_list(request):
    search_query = request.GET.get('search', '')
    genre_filter = request.GET.get('genre', '')
    author_filter = request.GET.get('author', '')
    status_filter = request.GET.get('status', '')

    books = Book.objects.all()

    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(genre__icontains=search_query)
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

@login_required
def student_dashboard(request):
    borrowed_books = BorrowedBook.objects.filter(user=request.user)
    return render(request, 'student_dashboard.html', {'borrowed_books': borrowed_books})


@login_required
def submit_rating(request, borrowed_book_id):
    borrowed_book = get_object_or_404(BorrowedBook, id=borrowed_book_id, user=request.user)
    if request.method == 'POST':
        form = RatingForm(request.POST, instance=borrowed_book)
        if form.is_valid():
            form.save()
            return redirect('student_dashboard')
    else:
        form = RatingForm(instance=borrowed_book)
    return render(request, 'submit_rating.html', {'form': form, 'borrowed_book': borrowed_book})