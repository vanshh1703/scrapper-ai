from celery import Celery
from core.config import settings

celery_app = Celery(
    "priceintel_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.task_routes = {
    "scrapers.*": "main-queue",
}
