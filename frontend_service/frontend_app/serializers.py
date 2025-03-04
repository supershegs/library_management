import uuid
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import (
    Book,
    BorrowedBook, 
    ActiveUser
)


User = get_user_model()

class UserEnrollmentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User  # Fixed: lowercase 'model'
        fields = ['email', 'first_name', 'last_name', 'password']  # Fixed: changed 'field' to 'fields'

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


class UserLoginSerializer(serializers.Serializer):
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
            find_user = ActiveUser.objects.get(user=user)
            if find_user.is_session_expired() == True:
                find_user.session_id = session_id
                find_user.save()
            else:
                raise serializers.ValidationError({
                    "error":f"User is already in, use session_id: {find_user.session_id}"
                })
            
        except ActiveUser.DoesNotExist:
            ActiveUser.objects.create(
                user=user,
                session_id=session_id
            )
        data["user"] = user
        data["session_id"] = str(session_id) 
        return data
    
    
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'category', 'publisher', 'is_available']


class BookStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"  

    def create(self, validated_data):
        """
        Allow setting the 'id' manually when creating a book.
        """
        book_id = validated_data.pop("id", None) 
        book = Book(**validated_data)
        if book_id:
            book.id = book_id 
        book.save()
        return book

class BookCategoryFilterSerializer(serializers.Serializer):
    category = serializers.ChoiceField(
        choices=['fiction', 'technology', 'science'],
        required=True
    )
    
  
class BookPublisherFilterSerializer(serializers.Serializer):    
    publisher = serializers.ChoiceField(
        choices=['wiley', 'apress', 'manning'],
        required=True
    )
    
    
class SessionIDSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    duration_days= serializers.IntegerField()
    

class BorrowBookSerializer(serializers.ModelSerializer): 
    session_id = serializers.UUIDField(write_only=True)  # Hidden in response
    duration_days = serializers.IntegerField()

    class Meta:
        model = BorrowedBook
        fields = ['id','session_id', 'duration_days', 'borrowed_at','book', 'user']
        extra_kwargs = {
            'book': {'read_only': True},  
            'user': {'read_only': True},  
            'borrowed_at': {'read_only': True},
        }

    def create(self, validated_data):
        """
        Ensure that the borrowed book ID matches the book ID.
        """
        book = validated_data.pop('book')  
        borrowed_book = BorrowedBook.objects.create(book=book, **validated_data)
        return borrowed_book


    def to_representation(self, instance):  
        """Modify the response to show book and user details."""
        rep = super().to_representation(instance)

        # Ensure instance is a model instance, not a dictionary
        if isinstance(instance, dict):
            return rep  # Return as-is if it's a dictionary

        rep['book'] = {
            'id': instance.book.id,
            'title': instance.book.title,
            'author': instance.book.author,
        }
        rep['user'] = {
            'id': instance.user.id,
            'email': instance.user.email,
            'first_name': instance.user.first_name,
            
        }
        return rep
