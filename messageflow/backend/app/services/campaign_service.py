from app.repositories.campaigns import CampaignRepository
from app.repositories.templates import TemplateRepository
from app.repositories.datasets import DatasetRepository
from app.models.models import Campaign, Message
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.services.variable_resolver import VariableResolver
from app.workers.tasks import bulk_send_campaign_task

class CampaignService:
    def __init__(self, db: AsyncSession, company_id: str):
        self.db = db
        self.company_id = company_id
        self.repo = CampaignRepository(db, company_id=company_id)
        self.template_repo = TemplateRepository(db, company_id=company_id)
        self.dataset_repo = DatasetRepository(db, company_id=company_id)

    async def create_campaign(self, campaign_name: str, template_id: str, dataset_id: str):
        c = Campaign(id=str(uuid.uuid4()), company_id=self.company_id, campaign_name=campaign_name, template_id=template_id, dataset_id=dataset_id, status="draft")
        return await self.repo.create(c)

    async def preview(self, campaign_id: str, sample: int = 10):
        campaign = await self.repo.get(campaign_id)
        if not campaign:
            return None
        template = await self.template_repo.get(campaign.template_id)
        rows = await self.repo.get_customer_records(campaign.dataset_id, limit=sample)
        previews = []
        for r in rows:
            text = VariableResolver.render(template.template_content, r.dynamic_fields, fallback="")
            previews.append({"customer_id": r.id, "message": text})
        return previews

    async def send(self, campaign_id: str, schedule_at: str | None = None):
        campaign = await self.repo.get(campaign_id)
        if not campaign:
            raise Exception("campaign not found")
        # enqueue send task
        # For now: we will call Celery task to bulk_send_campaign_task which will generate and send messages
        bulk_send_campaign_task.delay(str(campaign.company_id), campaign_id)
        # update status
        campaign.status = "running"
        await self.db.flush()
        await self.db.commit()
        return campaign
