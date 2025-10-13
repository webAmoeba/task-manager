import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.settings")

app = Celery("task_manager")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    # Simple task to ensure Celery is wired correctly.
    return f"Request: {self.request!r}"
