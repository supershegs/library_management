FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY backend_service/ .

RUN pip install --no-cache-dir -r requirements.txt
# RUN python manage.py collectstatic --noinput
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend_config.wsgi:application"]
