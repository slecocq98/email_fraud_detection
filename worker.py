from fastapi import FastAPI
from celery import Celery

from settings import settings


app = FastAPI()
celery = Celery("tasks", broker=settings.CELERY_BROKER_URL, include=["workers.tasks"])

# Configure Celery to use MongoDB for result storage
celery.config_from_object(settings, namespace="CELERY")
celery.conf.update(result_persistent=True)
celery.conf.update(task_track_started=True)
celery.conf.update(ignore_result=False)
celery.conf.update(task_reject_on_worker_lost=True)
celery.conf.update(worker_send_task_events=True)
celery.conf.update(worker_prefetch_multiplier=1)
celery.conf.update(
    mongodb_backend_settings={
        "host": settings.MONGO_HOST,
        "port": settings.MONGO_PORT,
        "database": settings.MONGO_DATABASE,
        "user": settings.MONGO_USERNAME,
        "password": settings.MONGO_PASSWORD,
        "taskmeta_collection": settings.CELERY_BACKEND_COL,
    }
)
celery.conf.update(timezone="Europe/Paris")
celery.conf.update(task_routes={"workers.tasks.*": {"queue": "queue"}})
