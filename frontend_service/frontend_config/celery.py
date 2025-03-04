import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend_config.settings')

celery_app = Celery('frontend_config')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()

