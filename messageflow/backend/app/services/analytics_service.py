from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.models import models
from sqlalchemy import insert, update
import uuid

async def aggregate_daily_metrics(db: AsyncSession, day: datetime | None = None):
    # aggregates messages by company for the given day (UTC)
    if day is None:
        day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start = day
    end = day + timedelta(days=1)

    q = select(
        models.Message.company_id,
        func.count(models.Message.id).label('total'),
        func.count(func.nullif(models.Message.status != 'delivered', True)).label('delivered'),
        func.count(func.nullif(models.Message.status != 'failed', True)).label('failed')
    ).where(
        models.Message.created_at >= start,
        models.Message.created_at < end
    ).group_by(models.Message.company_id)

    res = await db.execute(q)
    rows = res.all()
    for row in rows:
        company_id = row[0]
        total = int(row[1] or 0)
        # delivered and failed counts computed manually below
        delivered_q = select(func.count(models.Message.id)).where(models.Message.company_id == company_id, models.Message.status == 'delivered', models.Message.created_at >= start, models.Message.created_at < end)
        failed_q = select(func.count(models.Message.id)).where(models.Message.company_id == company_id, models.Message.status == 'failed', models.Message.created_at >= start, models.Message.created_at < end)
        dres = await db.execute(delivered_q)
        fres = await db.execute(failed_q)
        delivered = int(dres.scalar() or 0)
        failed = int(fres.scalar() or 0)
        # upsert into analytics_aggregates
        stmt = insert(models.AnalyticsAggregate).values(
            id=str(uuid.uuid4()),
            company_id=company_id,
            period_start=start,
            period_end=end,
            sent_count=total,
            delivered_count=delivered,
            failed_count=failed
        )
        await db.execute(stmt)
    await db.commit()
    return True
