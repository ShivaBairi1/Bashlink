from celery import Celery
from app.core.config import settings

celery = Celery(
    "messageflow",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery.conf.task_routes = {
    'app.workers.tasks.bulk_send_campaign_task': {'queue': 'default'},
    'app.workers.tasks.process_excel_import_task': {'queue': 'imports'},
    'app.workers.tasks.process_whatsapp_webhook_task': {'queue': 'webhooks'}
}
