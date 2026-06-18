from fastapi import APIRouter, Depends, HTTPException, Request
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.template import TemplateCreate, TemplateOut
from app.services.template_service import TemplateService
from app.utils.permissions import require_roles

router = APIRouter(prefix="/templates", tags=["templates"])

@router.post("/", response_model=TemplateOut)
async def create_template(payload: TemplateCreate, request: Request, db: AsyncSession = Depends(get_db), _=require_roles(["OWNER","MANAGER","ADMIN"])):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401)
    svc = TemplateService(db, user["company_id"])
    t = await svc.create_template(payload.template_name, payload.channel, payload.template_content)
    return {"id": t.id, "template_name": t.template_name, "channel": t.channel, "template_content": t.template_content, "status": t.status}
