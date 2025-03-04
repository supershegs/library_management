import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from celery import shared_task
from django.conf import settings
from .models import Book, CustomUser, BorrowedBook


load_dotenv()

# FRONTEND_SERVICE_URL = "http://frontend-service/api/books/" FRONTEND_BOOKLIST_URL
BACKEND_SERVICE_URL = f"{os.getenv('BACKEND_URL')}admin-end/api/v1/books"
BACKEND_SERVICE_LOGIN_URL = f"{os.getenv('BACKEND_URL')}admin-end/api/v1/login"
BACKEND_SERVICE_BORROWED_BOOK=f"{os.getenv('BACKEND_URL')}admin-end/api/v1/borrowed-books"
BACKEND_USER_SYNC_URL = f"{os.getenv('BACKEND_URL')}admin-end/api/v1/front-end/users"  

@shared_task
def sync_borrowed_book_updated(book_id):
    try:
        # Fetch borrow record from frontend service
        print('>>>>>>>>>22222: ', book_id)
        try:
            borrowed_book = BorrowedBook.objects.get(id=book_id)
            print('========= ',borrowed_book.id)
    
            return_date = borrowed_book.return_date
            formatted_return_date = (return_date - timedelta(days=1)).strftime("%Y-%m-%d")
            
            user_email = borrowed_book.user.email
            
            borrowed_book_data = {
                "id": borrowed_book.id,
                "user_email": user_email,
                "book": borrowed_book.book.id,
                'return_date': formatted_return_date,
                'duration_days': borrowed_book.duration_days,
                
            } 
            print('________', borrowed_book_data)

            if not user_email or not book_id:
                return "Invalid borrow record data."

            user = CustomUser.objects.get(email=user_email)
            
            url = f"{BACKEND_SERVICE_BORROWED_BOOK}/{book_id}/"  
            print(url)
            response = requests.post(url, json=borrowed_book_data)
            action = "created"
            print(response.json())
            
            if response.status_code in [200, 201]:
                return f"Book '{borrowed_book.book.title}' successfully {action} in frontend."
            else:
                return f"Failed to sync book '{borrowed_book.book.title}'. Response: {response.text}"

        except Book.CustomUser:
            return f"Book with ID {book_id} not found in backend."

    except Exception as e:
        return f"Error syncing borrow record: {str(e)}"
    

@shared_task
def sync_book_updated(book_id):
    """Sync added/updated book with frontend_service."""
    try:
        print('for borrowed book id>>>>: ', book_id)
        book = Book.objects.get(id=book_id)
        
        book_data = {
            "id": book.id,  
            "title": book.title,
            "author": book.author,
            "publisher": book.publisher,
            "category": book.category,
            "is_available": book.is_available,
            'available_copies': book.available_copies
        }

        print('>>>>>>>>>>>>>> ', book_data)
        
        frontend_book_url = f"{BACKEND_SERVICE_URL}/{book.id}/"  # Endpoint for updating book/getting book
        response = requests.get(frontend_book_url)
        
        print(frontend_book_url)
        
        if response.status_code != 200:
            return f"Failed to sync, book doesn't exit in the backend db"
        
        #login
        admin_login_details = {
            "email": os.getenv('admin_email'),
            "password": os.getenv('admin_password')
        }
        print(admin_login_details)
        session_id = None 
        res = requests.post(BACKEND_SERVICE_LOGIN_URL, admin_login_details)
        print('Admin Login response: ', res, res.json())
        resp = res.json()
        if res.status_code == 200:
            session_id = resp.get("data")['session_id']
        
        if res.status_code == 400:
            
            if resp.get('errors').get('session_id') != None:
                session_id = resp.get('errors')['session_id'][0]
            
            else:
                return f"Failed to sync, incorrect admin login details"
        
                        
        print('was book found ++++++: ', response.json(), response.status_code)
        edit_data = {
            "session_id": session_id,
            "title": book.title,
            "author": book.author,
            "publisher": book.publisher,
            "category": book.category,
            "is_available": book.is_available,
            "available_copies": book.available_copies
        }
        response = requests.put(frontend_book_url, json=edit_data)
        action = "updated"
        

        if response.status_code in [200, 201]:
            return f"Book '{book.title}' successfully {action} in frontend."
        else:
            return f"Failed to sync book '{book.title}'. Response: {response.text}"

    except Book.DoesNotExist:
        return f"Book with ID {book_id} not found in backend."

    except requests.RequestException as e:
        return f"Error syncing book with frontend: {str(e)}"

    

@shared_task
def sync_user_with_backend(user_data):
    """Send user details to backend service."""
    try:
        print(f"Syncing user to backend: {user_data}")
        response = requests.post(BACKEND_USER_SYNC_URL, json=user_data, timeout=5)
        print(f"Backend Response: {response.status_code} - {response.text}")

        if response.status_code == 201:
            return f"User {user_data['email']} synced successfully."
        else:
            return f"Failed to sync user {user_data['email']}. Response: {response.text}"
    
    except requests.RequestException as e:
        return f"Error syncing user {user_data['email']} to backend: {str(e)}"    

    
    