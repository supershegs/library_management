from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import (
    Book, 
    CustomUser, 
    BorrowRecord,
    ActiveAdmin,
    FrontendUser
)

from .serializers import (
    BookSerializer, 
    UserSerializer, 
    BorrowRecordSerializer,
    AdminEnrollmentSerializer,
    AdminLoginSerializer,
    SessionIDSerializer,
    FrontendUserSerializer,
    
    BorrowedBoookSerializer,FrontendUserBorrowedBooksSerializer, UnavailableBookSerializer
)

from .utils import ApiResponse
class AdminEnrollmentView(APIView):
    @extend_schema(
        request=AdminEnrollmentSerializer, 
        responses={201: AdminEnrollmentSerializer},
        methods=["POST"],
        tags=["Admin enrollment and login"],
        description="Enroll a new admin with email, first name , last name and password"
    )
    
    def post(self, request):
        serializer = AdminEnrollmentSerializer(data=request.data)
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
    
class AdminLoginView(APIView):
    @extend_schema(
        request=AdminLoginSerializer,
            responses={
                200: OpenApiResponse(response=AdminLoginSerializer, description="Login successfully."),
                400: OpenApiResponse(description="Login failed.")
            },
            methods=["POST"],
            tags=["Admin enrollment and login"],
            description="Login with your email, and password"
    )
    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
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
        # print('===========',serializer.errors.get("session_id")[0])
        return ApiResponse.failure(
            msg="Login failed.",
            status= 400,
            errors=serializer.errors
        )

    


class FrontendUserAPIView(APIView):
    @extend_schema(exclude=True)
    def post(self, request):
        serializer = FrontendUserSerializer(data=request.data)
        try:
            if serializer.is_valid():
                user = serializer.save()
                return ApiResponse.success(
                    msg="User successfully synced with backend.",
                    status = 201,
                    data= FrontendUserSerializer(user).data,
                )
            return ApiResponse.failure(
                msg= "Failed to sync user.", 
                status= 400,
                errors =serializer.errors
            )
        except Exception as e:
            return ApiResponse.failure(
                msg="User registration  synced failed.",
                status= 400,
                errors=str(e)
            )

    
    @extend_schema(
        responses={200: FrontendUserSerializer(many=True)},
        methods=["GET"],
        tags=["Frontend user"],
        summary="Fetch list of frontend users Enrolled in the Library "
    )
    def get(self, request):
        try: 
            users = FrontendUser.objects.all()
            serializer = FrontendUserSerializer(users, many=True)
            return ApiResponse.success(
                msg="get all frontend user.",
                status = 201,
                data= serializer.data,
            )
        except Exception as e:
            return ApiResponse.failure(
                msg="failed to get user.",
                status= 400,
                errors=str(e)
            )
class AddBookAPIView(APIView):
    @extend_schema(
        request=BookSerializer, responses={201: BookSerializer},
        tags=["admin books"],
        methods=['POST'],
        summary="Add/create new book"
    )
    def post(self, request):
        try:
            serializer = BookSerializer(data=request.data)
            if serializer.is_valid():
                
                # session_id = serializer.validated_data["session_id"]
                session_id = serializer.validated_data.pop("session_id")
                
                active_user = ActiveAdmin.objects.get(session_id= session_id)
                user = CustomUser.objects.get(email=active_user.user.email)
                if active_user.is_session_expired() == True:
                    return ApiResponse.failure(
                        msg="failed to validate user",
                        status= 400,
                        errors="session id expired: user need to login"
                    )
            
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


class EditAPIView(APIView):
    @extend_schema(
        request=BookSerializer, 
        responses={200: BookSerializer},
        tags=["admin books"],
        methods=['PUT'],
        summary="Edit/update an existing book details"
    )
    def put(self, request, book_id):
        try:
            serializer = BookSerializer(data=request.data, partial=True)
            if serializer.is_valid():
            
                session_id = serializer.validated_data.pop("session_id")
                    
                active_user = ActiveAdmin.objects.get(session_id= session_id)
                if active_user.is_session_expired() == True:
                    return ApiResponse.failure(
                        msg="failed to validate user",
                        status= 400,
                        errors="session id expired: user need to login"
                    )
                    
                book = Book.objects.get(id=book_id, is_available=True)
                serializer = BookSerializer(book, data=request.data, partial=True)         
                
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
        except ActiveAdmin.DoesNotExist:
            return ApiResponse.failure(msg="user not login",status= 500)
        except Book.DoesNotExist:
            return ApiResponse.failure(msg="Book not found",status= 500)
        except Exception as e:
            return ApiResponse.failure(
                msg="failed.",
                status= 500,
                errors=str(e)
            )


    @extend_schema(
        responses={200: BookSerializer},
        tags=["admin books"],
        methods=['GET'],
        summary="Get details of a single book by ID"
    )
    
    # you can access without session id
    def get(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)
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
    
    
    @extend_schema(
        request=SessionIDSerializer,
        responses={
            200: OpenApiResponse(description="Book successfully deleted."),
            400: OpenApiResponse(description="Failed to validate user (session expired)."),
            404: OpenApiResponse(description="Book not found."),
            500: OpenApiResponse(description="An error occurred.")
        },
        # methods=['DELETE'],
        tags=["admin books"], 
        summary="Delete book by ID"
    ) 
    def delete(self, request, book_id):
        try:
            serializer = SessionIDSerializer(data=request.data)
            if serializer.is_valid():
                session_id = serializer.validated_data["session_id"]
                
                active_user = ActiveAdmin.objects.get(session_id= session_id) 
                if active_user.is_session_expired() == True:
                    return ApiResponse.failure(
                        msg="failed to validate user",
                        status= 400,
                        errors="session id expired: user need to login"
                    )
            
                book = Book.objects.get(id=book_id)
                book.delete()
                return ApiResponse.success(msg="book successfully deleted.",status = 200)
            return ApiResponse.failure(msg="failed",status= 500, errors=serializer.errors)
        except Book.DoesNotExist:
            return ApiResponse.failure(msg="Book not found",status= 500)
        except ActiveAdmin.DoesNotExist:
            return ApiResponse.failure(msg="user not login",status= 500)
        except Exception as e:
            return ApiResponse.failure(
                msg="failed.",
                status= 500,
                errors=str(e)
            )


class ListBooksView(APIView):
    @extend_schema(
        responses={200: BookSerializer(many=True)},
        tags=["admin books"],
        methods=['GET'],
        summary="Admin to view list all available books"
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





class BorrowBookAPIView(APIView):
    @extend_schema(exclude=True)
    def post(self, request, book_id):
        try: 
            serializer = BorrowRecordSerializer(data=request.data)
            if serializer.is_valid():
                id = serializer.validated_data["id"]
                user_email = serializer.validated_data.get("user_email")
                book = serializer.validated_data["book"]
                return_date = serializer.validated_data["return_date"]
                duration_days = serializer.validated_data['duration_days']
                
                borrowed_book = BorrowRecord.objects.create(
                    id= id,
                    user_email=user_email,
                    book=book,
                    return_date= return_date,
                    duration_days= duration_days
                )
                return ApiResponse.success(
                        msg="Book successfully borrowed.",
                        status=201,
                        # data=BorrowRecordSerializer(borrowed_book).data,  
                        data=serializer.data
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

    @extend_schema(
        methods=['DELETE'],
        tags=["admin borrow books"], 
        summary="delete user borrowed books by ID"
    ) 
    def delete(self, request, book_id):
        try:
            borrowed_book = BorrowRecord.objects.get(id=book_id)
            book = Book.objects.get(id= borrowed_book.book.id)
            
            book.available_copies += 1
            if book.available_copies >=1:
                book.is_available = True
            else: 
                book.is_available = False
            borrowed_book.delete()
            book.save()
            return ApiResponse.success(msg="book successfully deleted.",status = 200)
        except BorrowRecord.DoesNotExist:
            return ApiResponse.failure(msg="Book borrowed not found",status= 500)
    
        except Book.DoesNotExist:
            return ApiResponse.failure(msg="Book not found",status= 500)


class ListUsersWithBorrowedBooksAPIView(APIView):
    @extend_schema(
        methods=['GET'],
        tags=["admin borrow books"], 
        summary="Fetched list of borrowed books records"
    )
    def get(self, request):
        try:
            records = BorrowRecord.objects.all()
            serializer = BorrowRecordSerializer(records, many=True)
            return ApiResponse.success(
                msg="book successfully Fetch.",
                status = 200,
                data=serializer.data,
            )
        except Book.DoesNotExist:
            return ApiResponse.failure(msg="Book not found",status= 500)
class ListUnavailableBooksAPIView(APIView):
    @extend_schema(
        responses={201: UnavailableBookSerializer},
        methods=['GET'],
        tags=["admin borrow books"], 
        summary="list books that is unavailable"
    )
    def get(self, request):
        try:
            unavailable_books = Book.objects.filter(is_available=False)
            # unavailable_books = Book.objects.filter(is_available=False) | Book.objects.filter(available_copies=0)
            serializer = UnavailableBookSerializer(unavailable_books, many=True)
            return ApiResponse.success(
                msg="Unavailable book list fetched successfully",
                status = 200,
                data=serializer.data,
            )
        except Exception as e:
            return ApiResponse.failure(
                msg="failed.",
                status= 400,
                errors=str(e)
            )


class FrontUserBorrowedBooksView(APIView):
    @extend_schema(
        responses={201: FrontendUserBorrowedBooksSerializer},
        methods=["GET"],
        tags=["Frontend user"],
        summary="Fetch list of frontend users and the books they have borrowed"
    )
    def get(self, request):
        try: 
            users = FrontendUser.objects.all()
            serializer = FrontendUserBorrowedBooksSerializer(users, many=True)
            return ApiResponse.success(
                msg="Frontend users alongg with the list of their borrowed books successfully Fetch.",
                status = 200,
                data=serializer.data,
            )
        except Exception as e:
            return ApiResponse.failure(
                msg="failed.",
                status= 400,
                errors=str(e)
            )