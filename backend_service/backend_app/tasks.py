import requests
import os
from celery import shared_task
from django.conf import settings
from .models import Book
from dotenv import load_dotenv

load_dotenv()

# FRONTEND_SERVICE_URL = "http://frontend-service/api/books/" FRONTEND_BOOKLIST_URL
FRONTEND_SERVICE_URL = f"{os.getenv('FRONTEND_URL')}user-end/api/v1/books"
FRONTEND_ADD_BOOK_URL = f"{os.getenv('FRONTEND_URL')}user-end/api/v1/books"
FRONTEND_BORROWED_BOOK_URL = f"{os.getenv('FRONTEND_URL')}user-end/api/v1/borrowed-books"

@shared_task
def sync_book_with_frontend(book_id):
    """Sync added/updated book with frontend_service."""
    try:
        print('for book id>>>>: ', book_id)
        book = Book.objects.get(id=book_id)
        is_available = None
        
        if book.available_copies >= 1:
            is_available = True
        else:
            is_available = False
        
        book_data = {
            "id": book.id,  # Ensure backend ID is sent to frontend
            "title": book.title,
            "author": book.author,
            "publisher": book.publisher,
            "category": book.category,
            "is_available": is_available,
            'available_copies': book.available_copies
        }

        print('>>>>>>>>>>>>>> ', book_data)
        
        frontend_book_url = f"{FRONTEND_SERVICE_URL}/{book.id}/"  # Endpoint for updating book/getting book
        response = requests.get(frontend_book_url)
        print(frontend_book_url)
        print('was book found ++++++: ', response.json(), response.status_code)
        
        if response.status_code == 200:
            edit_data = {
                "title": book.title,
                "author": book.author,
                "publisher": book.publisher,
                "category": book.category,
                "is_available": is_available,
                "available_copies": book.available_copies
            }
            response = requests.put(frontend_book_url, json=edit_data)
            action = "updated"
        else:
            # Book does not exist, create a new entry
            frontend_add_book_url = f"{FRONTEND_SERVICE_URL}/add"
            response = requests.post(frontend_add_book_url, json=book_data)
            action = "created"


        if response.status_code in [200, 201]:
            return f"Book '{book.title}' successfully {action} in frontend."
        else:
            return f"Failed to sync book '{book.title}'. Response: {response.text}"

    except Book.DoesNotExist:
        return f"Book with ID {book_id} not found in backend."

    except requests.RequestException as e:
        return f"Error syncing book with frontend: {str(e)}"

    

@shared_task
def delete_book_from_frontend(book_id):
    """Sync book deletion with frontend_service."""
    try:
        print('for book id>>>>: ', book_id)
        print('url ------: ', FRONTEND_SERVICE_URL)
        response = requests.delete(f"{FRONTEND_SERVICE_URL}/{book_id}/", timeout=5)
        response.raise_for_status()
        return f"Book {book_id} deleted from frontend successfully."
    except Exception as e:
        return f"Failed to delete book {book_id} from frontend: {str(e)}"
    
    
@shared_task
def delete_borrowed_book_from_frontend(book_id):
    """Sync borrowed book deletion with frontend_service."""
    try:
        print('for borrowed book id>>>>: ', book_id)
        borrowed_booked_delete_url= f"{FRONTEND_BORROWED_BOOK_URL}/{book_id}/"
        print('**************: ',borrowed_booked_delete_url)
        response = requests.delete(borrowed_booked_delete_url, timeout=5)
        print('response >>>>>>>>>>>==: ',response.json())
        response.raise_for_status()
        return f"Borrowed book {book_id} deleted from frontend successfully."
    except Exception as e:
        return f"Failed to delete book {book_id} from frontend: {str(e)}"

