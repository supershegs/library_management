from django.urls import path
from .views import (
    AdminEnrollmentView,
    AdminLoginView,
    AddBookAPIView,
    EditAPIView, 
    ListBooksView,
    BorrowBookAPIView,
    FrontendUserAPIView,
    ListUsersWithBorrowedBooksAPIView, 
    FrontUserBorrowedBooksView,
    ListUnavailableBooksAPIView
)

urlpatterns = [
    path('register', AdminEnrollmentView.as_view(), name='admin-register'),
    path('login', AdminLoginView.as_view(), name='admin-login'),
    path('front-end/users', FrontendUserAPIView.as_view()),
    
    path('books', ListBooksView.as_view(), name='book'),
    path('books/add', AddBookAPIView.as_view(), name='book-add'),
    path('books/<int:book_id>/', EditAPIView.as_view(), name='book-details'),
    path('borrowed-books/<int:book_id>/', BorrowBookAPIView.as_view()),
    path('borrowed-books', ListUsersWithBorrowedBooksAPIView.as_view(), name='list-users-borrowed-books'),
    path('borrowed-books/users', FrontUserBorrowedBooksView.as_view()),
    
    path('books/unavailable', ListUnavailableBooksAPIView.as_view(), name='list-unavailable-books'),
]
