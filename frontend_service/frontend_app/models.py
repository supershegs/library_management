import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.first_name


class BaseModel(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        
class ActiveUser(BaseModel): 
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    session_id = models.UUIDField(default=uuid.uuid4, unique=True)
    
    SESSION_EXPIRY_MINUTES = 15
    
    def is_session_expired(self):
        expiry_time = self.updatedAt + timedelta(minutes=self.SESSION_EXPIRY_MINUTES)
        return timezone.now() > expiry_time
    
    # def __str__(self):
    #     return self.session_id 
        
class Book(BaseModel):
    CATEGORY_CHOICES = [
        ('fiction', 'Fiction'),
        ('technology', 'Technology'),
        ('science', 'Science'),
    ]
    PUBLISHER_CHOICES = [
        ('wiley', 'Wiley'),
        ('apress', 'Apress'),
        ('manning', 'Manning'),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    publisher = models.CharField(max_length=50, choices=PUBLISHER_CHOICES)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class BorrowedBook(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    duration_days = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.email} borrowed {self.book.title}"
