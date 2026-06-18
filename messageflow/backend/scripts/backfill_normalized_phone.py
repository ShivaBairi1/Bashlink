import asyncio
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.models import CustomerRecord
from app.utils.phones import normalize_phone
from sqlalchemy import select, update
from app.models import models

DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(DATABASE_URL, future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def backfill():
    async with AsyncSessionLocal() as session:
        q = select(models.CustomerRecord).where(models.CustomerRecord.normalized_phone == None)
        res = await session.execute(q)
        rows = res.scalars().all()
        print(f"Found {len(rows)} records to backfill")
        for r in rows:
            phone = r.phone
            normalized = normalize_phone(phone)
            # try common dynamic fields
            if not normalized and isinstance(r.dynamic_fields, dict):
                for key in ['phone','Phone','Mobile','mobile','msisdn']:
                    val = r.dynamic_fields.get(key)
                    if val:
                        normalized = normalize_phone(val)
                        if normalized:
                            break
            if normalized:
                await session.execute(update(models.CustomerRecord).where(models.CustomerRecord.id == r.id).values(normalized_phone=normalized))
        await session.commit()
        print('Backfill complete')

if __name__ == '__main__':
    asyncio.run(backfill())
