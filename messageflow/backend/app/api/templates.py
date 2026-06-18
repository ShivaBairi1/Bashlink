from fastapi import APIRouter, Depends, HTTPException, Request
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.template import TemplateCreate, TemplateOut
from app.services.template_service import TemplateService

router = APIRouter(prefix="/templates", tags=["templates"])

@router.post("/", response_model=TemplateOut)
async def create_template(payload: TemplateCreate, request: Request, db: AsyncSession = Depends(get_db)):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401)
    svc = TemplateService(db, user["company_id"])
    t = await svc.create_template(payload.template_name, payload.channel, payload.template_content)
    return {"id": t.id, "template_name": t.template_name, "channel": t.channel, "template_content": t.template_content, "status": t.status}

@router.get("/", response_model=list[TemplateOut])
async def list_templates(request: Request, db: AsyncSession = Depends(get_db)):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401)
    svc = TemplateService(db, user["company_id"])
    items = await svc.repo.list()
    out = []
    for t in items:
        out.append({"id": t.id, "template_name": t.template_name, "channel": t.channel, "template_content": t.template_content, "status": t.status})
    return out

@router.get("/{template_id}", response_model=TemplateOut)
async def get_template(template_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401)
    svc = TemplateService(db, user["company_id"])
    t = await svc.repo.get(template_id)
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"id": t.id, "template_name": t.template_name, "channel": t.channel, "template_content": t.template_content, "status": t.status}

@router.put("/{template_id}", response_model=TemplateOut)
async def update_template(template_id: str, payload: TemplateCreate, request: Request, db: AsyncSession = Depends(get_db)):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401)
    svc = TemplateService(db, user["company_id"])
    await svc.repo.update(template_id, template_name=payload.template_name, template_content=payload.template_content, channel=payload.channel)
    t = await svc.repo.get(template_id)
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"id": t.id, "template_name": t.template_name, "channel": t.channel, "template_content": t.template_content, "status": t.status}

@router.delete("/{template_id}")
async def delete_template(template_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401)
    svc = TemplateService(db, user["company_id"])
    await svc.repo.delete(template_id)
    return {"status": "deleted"}
