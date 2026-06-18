from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

class BaseRepository:
    def __init__(self, session: AsyncSession, company_id: Optional[str] = None):
        self.session = session
        self.company_id = company_id

    def ensure_tenant(self, model_cls):
        # For safety: repository methods must apply company_id filter; this is helper
        if not self.company_id:
            raise Exception("company_id not provided to repository (tenant enforcement).")
