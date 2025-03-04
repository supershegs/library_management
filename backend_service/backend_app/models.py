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
        
class ActiveAdmin(BaseModel): 
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    session_id = models.UUIDField(default=uuid.uuid4, unique=True)
    
    SESSION_EXPIRY_MINUTES = 120
    
    def is_session_expired(self):
        expiry_time = self.updatedAt + timedelta(minutes=self.SESSION_EXPIRY_MINUTES)
        return timezone.now() > expiry_time

class FrontendUser(BaseModel):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.email

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
 
 
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    publisher = models.CharField(max_length=50, choices=PUBLISHER_CHOICES)
    is_available = models.BooleanField(default=True)
    available_copies = models.PositiveIntegerField(default=1)
    

    def __str__(self):
        return self.title


class BorrowRecord(BaseModel):
    id = models.IntegerField(primary_key=True)
    user_email = models.CharField(max_length=255, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField()
    duration_days = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user_email} borrowed {self.book.title}"
    
    @property
    def due_days(self):
        today_date = timezone.now().date()
        return (self.return_date - today_date).days
