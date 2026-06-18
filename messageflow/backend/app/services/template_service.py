from app.repositories.templates import TemplateRepository
from app.models.models import Template
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.services.variable_resolver import VariableResolver

class TemplateService:
    def __init__(self, db, company_id):
        self.db = db
        self.repo = TemplateRepository(db, company_id=company_id)
        self.company_id = company_id

    async def create_template(self, template_name: str, channel: str, template_content: str):
        tmpl = Template(id=str(uuid.uuid4()), company_id=self.company_id, template_name=template_name, channel=channel, template_content=template_content)
        return await self.repo.create(tmpl)

    async def validate_template(self, template_content: str, dataset_columns: list):
        tokens = VariableResolver.extract_tokens(template_content)
        missing = [t for t in tokens if t not in dataset_columns]
        return {"tokens": tokens, "missing": missing}
