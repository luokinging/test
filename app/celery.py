import os
from celery import Celery

if "DJANGO_SETTINGS_MODULE" not in os.environ:
    raise RuntimeError("DJANGO_SETTINGS_MODULE environment variable is not set")

# App name usually matches the project name
app = Celery("app")

# Load configuration from Django settings
# namespace='CELERY' means that in settings.py,
# all Celery-related configurations must start with CELERY_ (e.g., CELERY_BROKER_URL)
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
