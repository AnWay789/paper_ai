import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paper_ai.config.settings')
app = Celery('paper_ai')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
