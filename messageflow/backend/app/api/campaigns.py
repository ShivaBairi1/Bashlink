from fastapi import APIRouter, Depends, Request, HTTPException
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.campaign_service import CampaignService
from app.schemas.campaign import CampaignCreate, CampaignOut, CampaignPreviewRequest
from app.utils.permissions import require_roles

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

@router.post("/", response_model=CampaignOut)
async def create_campaign(payload: CampaignCreate, request: Request, db: AsyncSession = Depends(get_db), _=require_roles(["OWNER","MANAGER","ADMIN"])):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401)
    svc = CampaignService(db, user["company_id"])
    c = await svc.create_campaign(payload.campaign_name, payload.template_id, payload.dataset_id)
    return {"id": c.id, "campaign_name": c.campaign_name, "status": c.status}
