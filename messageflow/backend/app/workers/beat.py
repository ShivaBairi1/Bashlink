from celery.schedules import crontab
from app.workers.celery_app import celery
from app.services.analytics_service import aggregate_daily_metrics
from app.database.session import async_session
from datetime import datetime

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # run daily aggregation at 00:05 UTC
    sender.add_periodic_task(crontab(hour=0, minute=5), run_daily_analytics.s())

@celery.task
def run_daily_analytics():
    # run aggregation synchronously via an async session
    async def _run():
        async with async_session() as db:
            await aggregate_daily_metrics(db, datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0))
    import asyncio
    asyncio.run(_run())
