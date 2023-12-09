from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab # type: ignore

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EagleVision.settings')

app = Celery('EagleVision')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.

app.config_from_object('django.conf:settings', namespace='CELERY')


# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


app.conf.beat_schedule = {
    #Scheduler Name
    'send_emails_through_django': {
        # Task Name (Name Specified in Decorator)
        'task': 'watchlist.tasks.send_emails',  
        # Schedule      
        'schedule': 60.0
    },
    'check_new_classes': {
        'task': 'searchPage.tasks.check_classes',
        # 'schedule': crontab(hour='*/12') # run every 12 hours
        'schedule': 60.0
    }
}