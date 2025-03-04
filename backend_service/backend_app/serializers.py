import uuid
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

from .models import Book, CustomUser, BorrowRecord, ActiveAdmin, FrontendUser


User = get_user_model()



class AdminEnrollmentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User 
        fields = ['email', 'first_name', 'last_name', 'password']  

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError({
                "error":"A user with this email already exists."
            })  # Fixed grammar
        return value

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['email'],  # Using email as username
            is_active=True
        )
        user.set_password(validated_data['password'])  # Hash password before saving
        user.save()
        return user

class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise serializers.ValidationError({
                "error":"Email and password are required."
            })

        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError({
                "error":"Invalid email or password."
            })
        
        session_id = uuid.uuid4()
        
        try:
            find_user = ActiveAdmin.objects.get(user=user)
            if find_user.is_session_expired() == True:
                find_user.session_id = session_id
                find_user.save()
            else:
                raise serializers.ValidationError({
                    "error":f"User is already in, use below session ID",
                    "session_id": find_user.session_id
                    
                })
            
        except ActiveAdmin.DoesNotExist:
            ActiveAdmin.objects.create(
                user=user,
                session_id=session_id
            )
        data["user"] = user
        data["session_id"] = str(session_id) 
        return data



class FrontendUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrontendUser
        fields = ["id", "email", "first_name", "last_name"]
        extra_kwargs = {
            "id": {"read_only": True},  
            "created_at": {"read_only": True}
        }

    def create(self, validated_data):
        """Create user if they do not exist, otherwise update details."""
        user, created = FrontendUser.objects.update_or_create(
            email=validated_data["email"],  # Use email as unique identifier
            defaults={
                "first_name": validated_data["first_name"],
                "last_name": validated_data["last_name"],
            },
        )
        return user

class SessionIDSerializer(serializers.Serializer):
    session_id = serializers.UUIDField(write_only=True)
    
    

class BookSerializer(serializers.ModelSerializer):
    session_id = serializers.UUIDField(write_only=True)
    category = serializers.ChoiceField(choices=Book.CATEGORY_CHOICES)
    publisher = serializers.ChoiceField(choices=Book.PUBLISHER_CHOICES)
    
    class Meta:
        model = Book
        fields = "__all__"
        
    def create(self, validated_data):
        validated_data.pop('session_id', None)
        return super().create(validated_data)


class UserSerializer(SessionIDSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"

class BorrowRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = BorrowRecord
        fields = "__all__"
    

class RefinedBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'category', 'publisher']
    
        
class BorrowedBoookSerializer(serializers.ModelSerializer):
    book = RefinedBookSerializer()  # Nested serializer to show book details
    due_days = serializers.ReadOnlyField()

    class Meta:
        model = BorrowRecord
        fields = ['book', 'borrow_date', 'return_date', 'duration_days', 'due_days']

        
class FrontendUserBorrowedBooksSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()  # Include user id
    borrowed_books = serializers.SerializerMethodField()

    class Meta:
        model = FrontendUser
        fields = ['id', 'email', 'first_name', 'last_name', 'borrowed_books']

    def get_borrowed_books(self, obj):
        borrowed_records = BorrowRecord.objects.filter(user_email=obj.email)
        return BorrowedBoookSerializer(borrowed_records, many=True).data


class UnavailableBookSerializer(serializers.ModelSerializer):
    available_on = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'category', 'publisher', 'available_on']

    def get_available_on(self, obj):
        latest_borrow = BorrowRecord.objects.filter(book=obj).order_by('-return_date').first()
        return latest_borrow.return_date if latest_borrow else None
