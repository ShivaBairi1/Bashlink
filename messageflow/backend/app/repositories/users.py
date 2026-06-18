from app.repositories.base import BaseRepository
from app.models.models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

class UserRepository(BaseRepository):
    async def create(self, user: User):
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_by_email(self, email: str) -> Optional[User]:
        q = select(User).where(User.email == email)
        res = await self.session.execute(q)
        return res.scalar_one_or_none()

    async def get(self, user_id: str) -> Optional[User]:
        q = select(User).where(User.id == user_id)
        res = await self.session.execute(q)
        return res.scalar_one_or_none()
