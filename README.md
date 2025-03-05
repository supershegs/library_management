# library_management
an application to manage books in a library


git clone https://github.com/supershegs/library_management.git

git fetch --all

switch dev branch: git checkout dev

<---To access the frontend_service---->
    -   cd frontend_service
    -   create virtual environment: python -m venv env
    -   switch to the newly created virtual environment:        env\Scripts\activate
    -   install all pip libraries: pip install -r requirements.txt
    -   To run frontend_service locally: python manage.py runserver
    -   To start celery work for the frontend_service: 
            from the cmd line inside the frontend_service directory run command: celery -A frontend_config worker --loglevel=info --pool=solo



<---- To access the backend_service ---->
    -   cd backend_service
    -   create virtual environment: python -m venv env
    -   switch to the newly created virtual environment:        env\Scripts\activate
    -   install all pip libraries: pip install -r requirements.txt
    -   To run backend_service locally: python manage.py runserver 127.0.0.1:5000
    -   To start celery work for the frontend_service: 
            from the cmd line inside the frontend_service directory run  celery -A backend_config worker --loglevel=info --pool=solo



<---- To access the backend_service ---->
    inside the root file(lbrary_management) run cmd line: docker-compose up --d




