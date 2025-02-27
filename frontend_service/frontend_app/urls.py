from django.urls import path


from .views import (
    UserEnrollmentView, 
    UserLoginView,
    ListBooksView,
    ListBooksByCategoryFilterView,
    ListBooksByPublisherFilterView,
    BookDetailAPIView,
    BorrowBookAPIView
    
)


urlpatterns = [
    path('register', UserEnrollmentView.as_view(), name='user-registration'),
    path('login', UserLoginView.as_view(), name='user-login'),
    
    path('booklist', ListBooksView.as_view(), name='list-books'),
    path('books/<int:book_id>/', BookDetailAPIView.as_view(), name='books-detail'),
    
    path('books-filtered-by-category', ListBooksByCategoryFilterView.as_view(), name='list--filtered-by-category'),
    path('books-filtered-by-publisher', ListBooksByPublisherFilterView.as_view(), name='list-books-filtered-by-publisher'),
    
    path('books/<int:book_id>/borrow', BorrowBookAPIView.as_view(), name='borrow-book')
    
]