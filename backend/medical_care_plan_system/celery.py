import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medical_care_plan_system.settings")

app = Celery("medical_care_plan_system")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
