from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('manage_books/', views.manage_books, name='manage_books'),
    path('manage_users/', views.view_users, name='view_users'),
    path('change_role/<int:user_id>/', views.change_role, name='change_role'),
    path('books/', views.list_books_student, name='list_books_student'),  # Student book list
    path('books/admin/', views.list_books_admin, name='list_books_admin'),  # Admin book list
    path('books/add/', views.add_book, name='add_book'),
    path('books/edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('books/delete/<int:book_id>/', views.delete_book, name='delete_book'),
    path('ban_student/<int:student_id>/', views.ban_student, name='ban_student'),  # Ban student
    path('view_books/', views.view_books, name='view_books'),
    path('list_books/', views.list_books, name='list_books'),  # Add this line for the list_books view
    path('role_redirect/', views.role_based_redirect, name='role_redirect'),
    path('superadmin_dashboard/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('view_users/', views.view_users, name='view_users'),
    path('book/<int:book_id>/submit_review/', views.submit_review, name='submit_review'),
    path('books/', views.book_list, name='book_list'),
    path('books/borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('books/return/<int:borrowed_book_id>/', views.return_book, name='return_book'),  # Add this line for the return_book view
    path('books/rate/<int:borrowed_book_id>/', views.submit_rating, name='submit_rating'),  # Add this line for the submit_rating view
    path('create_admin/', views.create_admin, name='create_admin'),
    path('manage_admins/', views.manage_admins, name='manage_admins'),
    path('manage_superadmins/', views.manage_superadmins, name='manage_superadmins'),
    path('delete_admin/<int:admin_id>/', views.delete_admin, name='delete_admin'),
    path('delete_superadmin/<int:superadmin_id>/', views.delete_superadmin, name='delete_superadmin'),
    path('change_role/<int:user_id>/', views.change_role, name='change_role'),
    path('student/borrowed_books/', views.student_borrowed_books, name='student_borrowed_books'),  # Student borrowed books
]