from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Book, BorrowRecord
from .tasks import sync_book_with_frontend, delete_book_from_frontend, delete_borrowed_book_from_frontend

@receiver(post_save, sender=Book)
def book_created_or_updated(sender, instance, created, **kwargs):
    """Trigger Celery task when a book is added or updated."""
    sync_book_with_frontend.delay(instance.id)

@receiver(post_delete, sender=Book)
def book_deleted(sender, instance, **kwargs):
    """Trigger Celery task when a book is deleted."""
    delete_book_from_frontend.delay(instance.id)
    
@receiver(post_delete, sender=BorrowRecord)
def borrowed_book(sender, instance, **kwargs):
    delete_borrowed_book_from_frontend.delay(instance.id)
