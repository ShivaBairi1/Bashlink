from pydantic import BaseModel
from typing import Optional

class CampaignCreate(BaseModel):
    campaign_name: str
    template_id: str
    dataset_id: str

class CampaignOut(BaseModel):
    id: str
    campaign_name: str
    status: str

class CampaignPreviewRequest(BaseModel):
    sample: int = 10
