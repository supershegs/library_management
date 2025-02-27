from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiResponse

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    UserEnrollmentSerializer, 
    UserLoginSerializer,
    BookSerializer,
    BorrowBookSerializer,
    BookCategoryFilterSerializer,
    BookPublisherFilterSerializer,
    SessionIDSerializer
)
from .models import (
    Book,
    BorrowedBook,
    CustomUser, ActiveUser
)
from .utils import ApiResponse
# Create your views here.



class UserEnrollmentView(APIView):
    @extend_schema(
        request=UserEnrollmentSerializer,
        responses={
            201: OpenApiResponse(response=UserEnrollmentSerializer, description="User registration successfully."),
            400: OpenApiResponse(description="User registration failed.")
        },
        methods=["POST"],
        tags=["User enrollment and login"],
        description="Enroll a new user with email, first name , last name and password"
    )
    def post(self, request):
        serializer = UserEnrollmentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return ApiResponse.success(
                        msg="User registration successfully.",
                        status = 201,
                        data=serializer.data
                    )
            except Exception as e:
                return ApiResponse.failure(
                    msg="User registration failed.",
                    status= 400,
                    errors=str(e)
                )
        return ApiResponse.failure(
            msg="User registration failed.",
            status= 400,
            errors=serializer.errors
        )   
        
        
class UserLoginView(APIView):
    @extend_schema(
        request=UserLoginSerializer,
            responses={
                200: OpenApiResponse(response=UserLoginSerializer, description="Login successfully."),
                400: OpenApiResponse(description="Login failed.")
            },
            methods=["POST"],
            tags=["User enrollment and login"],
            description="Login with your email, and password"
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.validated_data["user"]
                session_id = serializer.validated_data.get("session_id")

                data = {
                    'user': user.first_name,
                    "session_id": session_id
                }
                return ApiResponse.success(
                        msg="Login successfully.",
                        status = 200,
                        data=data,
                    )
                
            except Exception as e:
                return ApiResponse.failure(
                    msg="Login failed.",
                    status= 400,
                    errors=str(e)
                )
        return ApiResponse.failure(
            msg="Login failed.",
            status= 400,
            errors=serializer.errors
        )
    
    

class ListBooksView(APIView):
    @extend_schema(
        responses={200: BookSerializer(many=True)},
        tags=["Books"],
        summary="List all available books (without filters)"
    )
    def get(self, request):
        try:
            books = Book.objects.filter(is_available=True)
            serializer = BookSerializer(books, many=True)
            return ApiResponse.success(
                msg="books successfully Fetch.",
                status = 200,
                data=serializer.data,
            )
        except Exception as e:
            return ApiResponse.failure(
                msg="failed.",
                status= 400,
                errors=str(e)
            )
            
            
            
class ListBooksByCategoryFilterView(APIView):
    @extend_schema(
        request=BookCategoryFilterSerializer,
        responses={200: BookSerializer(many=True)},
        methods=["GET"],
        tags=["Books"],
        summary="get list of books with category as params",
        description="List all books filtered by category"
    )
    def get(self, request):
        serializer = BookCategoryFilterSerializer(data=request.query_params)
        if serializer.is_valid():
            try:
                category = serializer.validated_data['category']

                books = Book.objects.filter(category=category, is_available=True)
                serializer = BookSerializer(books, many=True)
                return ApiResponse.success(
                    msg="books successfully Fetch.",
                    status = 200,
                    data=serializer.data,
                )
            except Exception as e:
                return ApiResponse.failure(
                    msg="failed.",
                    status= 400,
                    errors=str(e)
                )
        return ApiResponse.failure(
            msg="failed.",
            status= 400,
            errors=serializer.errors
        )
        
        
class ListBooksByPublisherFilterView(APIView):
    @extend_schema(
        request=BookPublisherFilterSerializer,
        responses={200: BookSerializer(many=True)},
        methods=["GET"],
        tags=["Books"],
        summary="get list of books with publisher as params",
        description="List all books filtered by publisher"
    )
    def get(self, request):
        serializer = BookPublisherFilterSerializer(data=request.query_params)
        if serializer.is_valid():
            try:
                publisher = serializer.validated_data['publisher']

                books = Book.objects.filter(publisher=publisher, is_available=True)
                serializer = BookSerializer(books, many=True)
                return ApiResponse.success(
                    msg="books successfully Fetch.",
                    status = 200,
                    data=serializer.data,
                )
            except Exception as e:
                return ApiResponse.failure(
                    msg="failed.",
                    status= 400,
                    errors=str(e)
                )
        return ApiResponse.failure(
            msg="failed.",
            status= 400,
            errors=serializer.errors
        )


# Get Single Book by ID
class BookDetailAPIView(APIView):
    @extend_schema(
        responses={200: BookSerializer},
        tags=["Books"],
        summary="Get details of a single book by ID"
    )
    def get(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id, is_available=True)
            serializer = BookSerializer(book)
            return ApiResponse.success(
                    msg="book successfully Fetch.",
                    status = 200,
                    data=serializer.data,
                )
        except Exception as e:
            return ApiResponse.failure(
                msg="failed.",
                status= 400,
                errors=str(e)
            )

# Borrow Book by ID
class BorrowBookAPIView(APIView):
    @extend_schema(
        request=SessionIDSerializer,
        responses={201: BorrowBookSerializer},
        tags=["Borrow"],
        summary="Borrow a book by ID (specify duration in days)"
    )
    def post(self, request, book_id):
        try:
            serializer = SessionIDSerializer(data=request.data)
            if serializer.is_valid():
                session_id = serializer.validated_data.get("session_id")
                duration_days= serializer.validated_data['duration_days']

                book = Book.objects.get(id=book_id, is_available=True)
                
                active_user = ActiveUser.objects.get(session_id= session_id)
                user = CustomUser.objects.get(email=active_user.email)

                BorrowedBook.objects.create(
                    user=user,
                    book=book,
                    duration_days=duration_days
                )
                book.is_available = False  # Mark book as unavailable once borrowed
                book.save()
                return ApiResponse.success(
                    msg="book successfully Fetch.",
                    status = 200,
                    data=serializer.data,
                )
        
            return ApiResponse.failure(
                msg="failed.",
                status= 400,
                errors=serializer.errors
            )
        
        except Book.DoesNotExist:
            return ApiResponse.failure(
                msg="failed",
                status= 400,
                errors="Book not found or unavailable"
            )
        except CustomUser.DoesNotExist:
            return ApiResponse.failure(
                msg="failed.",
                status= 400,
                errors='User not found'
            )    
