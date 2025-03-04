from django.shortcuts import render
from drf_spectacular.utils import (
    extend_schema, 
    OpenApiResponse, 
    OpenApiParameter,
    OpenApiTypes
)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    UserEnrollmentSerializer, 
    UserLoginSerializer,
    BookSerializer,
    BookStoreSerializer,
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
from .tasks import sync_user_with_backend
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
                user = serializer.save()
                user_data = {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                }
                sync_user_with_backend.delay(user_data)
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
        methods=["GET"],
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
        parameters=[OpenApiParameter(
            name='category', location=OpenApiParameter.QUERY, required=True,
            description="fetch list of books by category(either fiction, technology, science)")
        ],
        responses={200: BookSerializer(many=True)},
        methods=["GET"],
        tags=["Books"],
        summary="List all books filtered by category",
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
        parameters=[OpenApiParameter(
            name='publisher', location=OpenApiParameter.QUERY, required=True,
            description="fetch list of books by publisher(either wiley, apress, manning )")
        ],
        responses={200: BookSerializer(many=True)},
        methods=["GET"],
        tags=["Books"],
        summary="List all books filtered by publisher"
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


# Borrow Book by ID
class BorrowBookAPIView(APIView):
    @extend_schema(
        request=BorrowBookSerializer,
        responses={201: BorrowBookSerializer},
        tags=["User Borrow Books"],
        summary="Borrow a book by ID (specify duration in days)"
    )
    def post(self, request, book_id):
        try:
            serializer = BorrowBookSerializer(data=request.data)
            
            if serializer.is_valid():
                session_id = serializer.validated_data.pop("session_id")  # Remove session_id from validated data
                
                active_user = ActiveUser.objects.get(session_id=session_id)
                if active_user.is_session_expired():
                    return ApiResponse.failure(
                        msg="Failed to validate user",
                        status=400,
                        errors="Session ID expired: user needs to log in"
                    )

                user = CustomUser.objects.get(email=active_user.user.email)                
                
                book = Book.objects.get(id=book_id, is_available=True)  
                
                if book.available_copies <= 0:
                    return ApiResponse.failure(
                        msg="Book not available.",
                        status=400,
                        errors="No copies left"
                    )
                
                borrowed_book = serializer.save(user=user, book=book)

                book.available_copies -= 1                
                if book.available_copies <= 0:
                    book.is_available = False
                else: 
                    book.is_available = True
                
                book.save()

                return ApiResponse.success(
                    msg="Book successfully borrowed.",
                    status=201,
                    data=BorrowBookSerializer(borrowed_book).data,  # Serialize instance, not `serializer.data`
                )

            return ApiResponse.failure(
                msg="Failed.",
                status=400,
                errors=serializer.errors
            )

        except ActiveUser.DoesNotExist:
            return ApiResponse.failure(
                msg="Failed.",
                status=400,
                errors="Session ID is invalid"
            )

        except CustomUser.DoesNotExist:
            return ApiResponse.failure(
                msg="Failed.",
                status=400,
                errors="User not found"
            )

        except Book.DoesNotExist:
            return ApiResponse.failure(
                msg="Failed",
                status=400,
                errors="Book not found or unavailable"
            )
   
    @extend_schema(exclude=True)
    def delete(self, request, book_id):
        try:
            borrowed_book = BorrowedBook.objects.get(id=book_id)
            book = Book.objects.get(id=borrowed_book.book.id)
            
            book.available_copies += 1
            if book.available_copies >=1:
                book.is_available = True
            else: 
                book.is_available = False
            book.save()
        
            borrowed_book.delete()
            return ApiResponse.success(msg="book successfully deleted.",status = 200)
        except BorrowedBook.DoesNotExist:
            return ApiResponse.failure(msg="Book borrowed not found",status= 500)
        
        except Book.DoesNotExist:
            return ApiResponse.failure(msg="Book not found",status= 500)

        
    
       
class AddBookAPIView(APIView):
    @extend_schema(exclude=True)
    def post(self, request):
        try:
            serializer = BookStoreSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ApiResponse.success(
                    msg="book successfully added.",
                    status = 201,
                    data=serializer.data,
                )      
            return ApiResponse.failure(
                msg="failed.",
                status= 400,
                errors=serializer.errors
            )
        except Exception as e:
            return ApiResponse.failure(
                msg="failed.",
                status= 500,
                errors= str(e)
            )

    
class EditBookAPIView(APIView):
    @extend_schema(exclude=True)
    
    
    def put(self, request, book_id):
        try:   
            book = Book.objects.get(id=book_id)
            serializer = BookStoreSerializer(book, data=request.data, partial=True)         
            if serializer.is_valid():
                serializer.save()
                return ApiResponse.success(
                        msg="book successfully edited.",
                        status = 200,
                        data=serializer.data,
                    )
            return ApiResponse.failure(
                msg="Failed to update book.",
                status=400,
                errors=serializer.errors
            )
        except Exception as e:
            return ApiResponse.failure(
                msg="failed.",
                status= 400,
                errors=str(e)
            )

    @extend_schema(
        responses={200: BookStoreSerializer},
        methods=['GET'],
        tags=["Books"],
        summary="Fetch book details by ID(single book)",
    )
    
    def get(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)
            serializer = BookStoreSerializer(book)
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
       
    @extend_schema(exclude=True)   
    def delete(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)
            book.delete()
            return ApiResponse.success(msg="book successfully deleted.",status = 200)
        except Book.DoesNotExist:
            return ApiResponse.failure(msg="Book not found",status= 500)