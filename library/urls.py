# library/urls.py

from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('manage_books/', views.manage_books, name='manage_books'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('change_role/<int:user_id>/', views.change_role, name='change_role'),
    path('books/', views.list_books, name='list_books'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('books/delete/<int:book_id>/', views.delete_book, name='delete_book'),
    path('ban_student/<int:student_id>/', views.ban_student, name='ban_student'),
    path('view_books/', views.view_books, name='view_books'),
    path('list_books/', views.list_books, name='list_books'),
    path('role_redirect/', views.role_based_redirect, name='role_redirect'),
    path('super_admin_dashboard/', views.superadmin_dashboard, name='super_admin_dashboard'),
    path('admin/manage_books/', views.manage_books, name='manage_books'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('view_users/', views.view_users, name='view_users'),
    path('book/<int:book_id>/submit_review/', views.submit_review, name='submit_review'),
    path('books/', views.book_list, name='book_list'),
    path('books/borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('books/return/<int:borrowed_book_id>/', views.return_book, name='return_book'),

]
