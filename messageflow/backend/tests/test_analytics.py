import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.analytics_service import aggregate_daily_metrics
from app.database.session import get_db

@pytest.mark.asyncio
async def test_aggregate_runs(get_test_db: AsyncSession):
    db: AsyncSession = get_test_db
    # run aggregation for today (no messages required) - should not error
    res = await aggregate_daily_metrics(db, datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0))
    assert res == True
