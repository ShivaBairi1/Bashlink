from fastapi import APIRouter, Depends, Request, HTTPException
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import models
from app.schemas.common import IDModel
from app.utils.permissions import require_roles
from sqlalchemy import select, delete

router = APIRouter(prefix="/admin/dlq", tags=["admin-dlq"])

@router.get('/', dependencies=[Depends(require_roles(["OWNER","ADMIN"]))])
async def list_dlq(db: AsyncSession = Depends(get_db), request: Request = None):
    user = getattr(request.state, 'user', None)
    company_id = user['company_id']
    q = select(models.ProviderFailedMessage).where(models.ProviderFailedMessage.company_id == company_id).order_by(models.ProviderFailedMessage.created_at.desc()).limit(200)
    res = await db.execute(q)
    rows = res.scalars().all()
    out = []
    for r in rows:
        out.append({"id": r.id, "message_id": r.message_id, "channel": r.channel, "error": r.error, "payload": r.payload, "created_at": r.created_at})
    return out

@router.post('/{dlq_id}/retry', dependencies=[Depends(require_roles(["OWNER","ADMIN"]))])
async def retry_dlq(dlq_id: str, db: AsyncSession = Depends(get_db), request: Request = None):
    user = getattr(request.state, 'user', None)
    company_id = user['company_id']
    q = select(models.ProviderFailedMessage).where(models.ProviderFailedMessage.id == dlq_id, models.ProviderFailedMessage.company_id == company_id)
    res = await db.execute(q)
    entry = res.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail='not found')
    # re-enqueue by creating a campaign message or re-sending directly; simplest: enqueue a worker task to reprocess payload
    from app.workers.tasks import process_dlq_retry_task
    process_dlq_retry_task.delay({"dlq_id": dlq_id})
    return {"status": "enqueued"}

@router.delete('/', dependencies=[Depends(require_roles(["OWNER","ADMIN"]))])
async def clear_dlq(db: AsyncSession = Depends(get_db), request: Request = None):
    user = getattr(request.state, 'user', None)
    company_id = user['company_id']
    await db.execute(delete(models.ProviderFailedMessage).where(models.ProviderFailedMessage.company_id == company_id))
    await db.commit()
    return {"status": "cleared"}
