from app.repositories.base import BaseRepository
from app.models.models import Dataset, CustomerRecord
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

class DatasetRepository(BaseRepository):
    async def create(self, dataset: Dataset):
        self.session.add(dataset)
        await self.session.flush()
        return dataset

    async def get(self, dataset_id: str) -> Dataset | None:
        q = select(Dataset).where(Dataset.id == dataset_id, Dataset.company_id == self.company_id)
        r = await self.session.execute(q)
        return r.scalar_one_or_none()

    async def list_for_company(self, limit: int = 50, offset: int = 0):
        q = select(Dataset).where(Dataset.company_id == self.company_id).limit(limit).offset(offset)
        r = await self.session.execute(q)
        return r.scalars().all()

    async def bulk_insert_records(self, records: List[Dict[str, Any]]):
        # Use SQLAlchemy core INSERT many for performance
        stmt = insert(CustomerRecord).values(records)
        await self.session.execute(stmt)
        await self.session.flush()
