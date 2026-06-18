from app.repositories.base import BaseRepository
from app.models.models import Campaign, Message, CustomerRecord
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from sqlalchemy import func

class CampaignRepository(BaseRepository):
    async def create(self, campaign: Campaign):
        self.session.add(campaign)
        await self.session.flush()
        return campaign

    async def get(self, campaign_id: str):
        q = select(Campaign).where(Campaign.id == campaign_id, Campaign.company_id == self.company_id)
        r = await self.session.execute(q)
        return r.scalar_one_or_none()

    async def list(self, limit: int = 50, offset: int = 0):
        q = select(Campaign).where(Campaign.company_id == self.company_id).limit(limit).offset(offset)
        r = await self.session.execute(q)
        return r.scalars().all()

    async def create_messages_bulk(self, messages: List[Dict]):
        stmt = insert(Message).values(messages)
        await self.session.execute(stmt)
        await self.session.flush()

    async def get_customer_records(self, dataset_id: str, limit: int = 1000, offset: int = 0):
        q = select(CustomerRecord).where(CustomerRecord.company_id == self.company_id, CustomerRecord.dataset_id == dataset_id).limit(limit).offset(offset)
        r = await self.session.execute(q)
        return r.scalars().all()
