from fastapi import APIRouter, Depends, Query
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.permissions import require_roles
from typing import Optional
from datetime import datetime
from app.services.analytics_service import aggregate_daily_metrics
from app.models import models
from sqlalchemy import select

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.post('/aggregate', dependencies=[Depends(require_roles(["OWNER","ADMIN"]))])
async def run_aggregate(db: AsyncSession = Depends(get_db), date: Optional[str] = Query(None)):
    # trigger aggregation for a date (YYYY-MM-DD) or today
    day = None
    if date:
        day = datetime.strptime(date, '%Y-%m-%d')
    await aggregate_daily_metrics(db, day)
    return {"status": "enqueued"}

@router.get('/dashboard', dependencies=[Depends(require_roles(["OWNER","ADMIN"]))])
async def get_dashboard(db: AsyncSession = Depends(get_db), date: Optional[str] = Query(None)):
    # return aggregated metrics for date
    day = None
    if date:
        day = datetime.strptime(date, '%Y-%m-%d')
    else:
        day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start = day
    end = day + timedelta(days=1)
    q = select(models.AnalyticsAggregate).where(models.AnalyticsAggregate.period_start == start)
    res = await db.execute(q)
    rows = res.scalars().all()
    out = []
    for r in rows:
        out.append({
            "company_id": r.company_id,
            "period_start": r.period_start,
            "period_end": r.period_end,
            "sent": r.sent_count,
            "delivered": r.delivered_count,
            "failed": r.failed_count
        })
    return out
