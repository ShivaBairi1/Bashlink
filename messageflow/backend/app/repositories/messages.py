from app.repositories.base import BaseRepository
from app.models.models import Message
from sqlalchemy import select, update

class MessageRepository(BaseRepository):
    async def update_status(self, message_id: str, status: str, provider_message_id: str | None = None):
        q = update(Message).where(Message.id == message_id, Message.company_id == self.company_id).values(status=status, provider_message_id=provider_message_id)
        await self.session.execute(q)
