# Library Management
An application to manage books in a library

## Clone Repository
```sh
git clone https://github.com/supershegs/library_management.git
git fetch --all
git checkout dev
```

## Accessing `frontend_service`
```sh
cd frontend_service
# Create virtual environment
python -m venv env
# Activate virtual environment
env\Scripts\activate
# Install dependencies
pip install -r requirements.txt
# Run frontend_service locally
python manage.py runserver
# Start Celery worker for frontend_service
(inside frontend_service)celery -A frontend_config worker --loglevel=info --pool=solo
```

## Accessing `backend_service`
```sh
cd backend_service
# Create virtual environment
python -m venv env
# Activate virtual environment
env\Scripts\activate
# Install dependencies
pip install -r requirements.txt
# Run backend_service locally
python manage.py runserver 127.0.0.1:5000
# Start Celery worker for backend_service
(inside backend_service)celery -A backend_config worker --loglevel=info --pool=solo
```

## Running with Docker(inside library management directory)
```sh
docker-compose up --d
```
