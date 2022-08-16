import os

from celery import Celery
from celery.schedules import crontab
 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
 
app = Celery('main')
app.config_from_object('django.conf:settings')

# app.conf.beat_schedule = {
#     "notify_users": {
#         "task": "bots.tasks.notify_users",
#         "schedule": crontab(minute='*/15')
#     }
# }

app.autodiscover_tasks()

# start celery:
# celery worker -A main --loglevel=debug --concurrency=4
