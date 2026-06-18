from sqlalchemy import update, select
from app.models.models import Company, CreditTransaction
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from sqlalchemy.sql import func

class CreditService:
    def __init__(self, db: AsyncSession, company_id: str):
        self.db = db
        self.company_id = company_id

    async def add_credits(self, amount: float):
        q = select(Company).where(Company.id == self.company_id)
        r = await self.db.execute(q)
        c = r.scalar_one_or_none()
        if not c:
            raise Exception("company not found")
        new_balance = (c.credits or 0) + amount
        await self.db.execute(update(Company).where(Company.id == self.company_id).values(credits=new_balance))
        tx = CreditTransaction(id=str(uuid.uuid4()), company_id=self.company_id, credits_added=amount, credits_used=0, balance_after=new_balance)
        self.db.add(tx)
        await self.db.flush()
        await self.db.commit()
        return new_balance

    async def consume_credits(self, amount: float):
        # non-atomic fallback
        q = select(Company).where(Company.id == self.company_id)
        r = await self.db.execute(q)
        c = r.scalar_one_or_none()
        if not c:
            raise Exception("company not found")
        if (c.credits or 0) < amount:
            raise Exception("insufficient credits")
        new_balance = (c.credits or 0) - amount
        await self.db.execute(update(Company).where(Company.id == self.company_id).values(credits=new_balance))
        tx = CreditTransaction(id=str(uuid.uuid4()), company_id=self.company_id, credits_added=0, credits_used=amount, balance_after=new_balance)
        self.db.add(tx)
        await self.db.flush()
        await self.db.commit()
        return new_balance

    async def consume_credits_atomic(self, amount: float):
        # atomic decrement: update where credits >= amount and return new balance
        stmt = (
            update(Company)
            .where(Company.id == self.company_id)
            .where(Company.credits >= amount)
            .values(credits=Company.credits - amount)
            .returning(Company.credits)
        )
        r = await self.db.execute(stmt)
        row = r.fetchone()
        if not row:
            raise Exception("insufficient credits")
        new_balance = row[0]
        tx = CreditTransaction(id=str(uuid.uuid4()), company_id=self.company_id, credits_added=0, credits_used=amount, balance_after=new_balance)
        self.db.add(tx)
        await self.db.flush()
        await self.db.commit()
        return new_balance
