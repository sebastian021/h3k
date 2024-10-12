import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hs3ck.settings')

app = Celery('hs3ck')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()