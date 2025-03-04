FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /app

COPY frontend_service/ .

RUN pip install --no-cache-dir -r requirements.txt

# RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "frontend_config.wsgi:application"]
