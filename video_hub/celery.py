import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_hub.settings')

app = Celery('video_hub')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.task_default_queue = 'default'
app.conf.task_default_exchange = 'default'
app.conf.task_default_routing_key = 'default'

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request}')
