from fastapi import APIRouter, Depends, Request, HTTPException
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import models
from app.schemas.common import IDModel
from app.utils.permissions import require_roles
from sqlalchemy import select

router = APIRouter(prefix="/admin/providers", tags=["admin-providers"])

@router.post('/', dependencies=[Depends(require_roles(["OWNER","ADMIN"]))])
async def create_whatsapp_config(payload: dict, db: AsyncSession = Depends(get_db), request: Request = None):
    user = getattr(request.state, 'user', None)
    if not user:
        raise HTTPException(status_code=401)
    company_id = user['company_id']
    phone_number_id = payload.get('phone_number_id')
    access_token = payload.get('access_token')
    if not phone_number_id or not access_token:
        raise HTTPException(status_code=400, detail='phone_number_id and access_token required')
    q = select(models.WhatsAppConfig).where(models.WhatsAppConfig.company_id == company_id)
    res = await db.execute(q)
    existing = res.scalar_one_or_none()
    if existing:
        await db.execute(update(models.WhatsAppConfig).where(models.WhatsAppConfig.id == existing.id).values(phone_number_id=phone_number_id, access_token=access_token))
    else:
        await db.execute(insert(models.WhatsAppConfig).values(id=str(os.urandom(16).hex()), company_id=company_id, phone_number_id=phone_number_id, access_token=access_token))
    await db.commit()
    return {"status": "ok"}

@router.get('/', dependencies=[Depends(require_roles(["OWNER","ADMIN"]))])
async def list_configs(db: AsyncSession = Depends(get_db), request: Request = None):
    user = getattr(request.state, 'user', None)
    company_id = user['company_id']
    q = select(models.WhatsAppConfig).where(models.WhatsAppConfig.company_id == company_id)
    res = await db.execute(q)
    cfg = res.scalar_one_or_none()
    if not cfg:
        return {}
    return {"phone_number_id": cfg.phone_number_id}

@router.delete('/', dependencies=[Depends(require_roles(["OWNER","ADMIN"]))])
async def delete_config(db: AsyncSession = Depends(get_db), request: Request = None):
    user = getattr(request.state, 'user', None)
    company_id = user['company_id']
    q = select(models.WhatsAppConfig).where(models.WhatsAppConfig.company_id == company_id)
    res = await db.execute(q)
    cfg = res.scalar_one_or_none()
    if cfg:
        await db.execute(delete(models.WhatsAppConfig).where(models.WhatsAppConfig.id == cfg.id))
        await db.commit()
    return {"status": "deleted"}
