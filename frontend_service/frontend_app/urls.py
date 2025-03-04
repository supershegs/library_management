from django.urls import path


from .views import (
    UserEnrollmentView, 
    UserLoginView,
    ListBooksView,
    ListBooksByCategoryFilterView,
    ListBooksByPublisherFilterView,
    BorrowBookAPIView,
    AddBookAPIView,
    EditBookAPIView
)


urlpatterns = [
    path('register', UserEnrollmentView.as_view(), name='user-registration'),
    path('login', UserLoginView.as_view(), name='user-login'),
    
    path('books', ListBooksView.as_view(), name='list-books'),   
    path('books-filtered-by-category', ListBooksByCategoryFilterView.as_view(), name='list--filtered-by-category'),
    path('books-filtered-by-publisher', ListBooksByPublisherFilterView.as_view(), name='list-books-filtered-by-publisher'),
    
    path('borrowed-books/<int:book_id>/', BorrowBookAPIView.as_view(), name='book-borrow'),
    
    path('books/add', AddBookAPIView.as_view(), name='books-add'),
    path('books/<int:book_id>/', EditBookAPIView.as_view(), name='books-edit'),

]