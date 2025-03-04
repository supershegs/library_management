from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Book, BorrowedBook

from .tasks import sync_book_updated, sync_borrowed_book_updated

@receiver(post_save, sender=BorrowedBook)
def borrowed_book_updated(sender, instance, created, **kwargs):
    """Trigger Celery task to update borrowed book record in backend database(DB)."""
    sync_borrowed_book_updated.delay(instance.id)

@receiver(post_save, sender=Book)
def book_updated(sender, instance, created, **kwargs):
    """Trigger Celery task to update book record in backend database(DB)."""
    sync_book_updated.delay(instance.id)
    

    
# sync_book_updated  and sync_borrowed_book_updated


# book_updated borrowed_book_updated

