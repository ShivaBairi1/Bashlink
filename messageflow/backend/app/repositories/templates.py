from app.repositories.base import BaseRepository
from app.models.models import Template
from sqlalchemy import select, update, delete

class TemplateRepository(BaseRepository):
    async def create(self, template: Template):
        self.session.add(template)
        await self.session.flush()
        return template

    async def get(self, template_id: str):
        q = select(Template).where(Template.id == template_id, Template.company_id == self.company_id)
        r = await self.session.execute(q)
        return r.scalar_one_or_none()

    async def list(self, limit: int = 50, offset: int = 0):
        q = select(Template).where(Template.company_id == self.company_id).limit(limit).offset(offset)
        r = await self.session.execute(q)
        return r.scalars().all()

    async def update(self, template_id: str, **fields):
        q = update(Template).where(Template.id == template_id, Template.company_id == self.company_id).values(**fields).returning(Template)
        r = await self.session.execute(q)
        await self.session.flush()
        return r.fetchone()

    async def delete(self, template_id: str):
        q = delete(Template).where(Template.id == template_id, Template.company_id == self.company_id)
        await self.session.execute(q)
        await self.session.flush()
