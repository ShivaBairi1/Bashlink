from fastapi import APIRouter, Request, HTTPException, status, Depends
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import models
from app.schemas.common import IDModel
from app.utils.security import decode_token

router = APIRouter()

@router.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.json()
    # Validate signature if provided (not implemented here)
    # Normalize events and process
    # Example: handle messages & statuses (very provider-specific)
    # This endpoint should publish an event to Celery for processing
    from app.workers.tasks import process_whatsapp_webhook_task
    process_whatsapp_webhook_task.delay(payload)
    return {"status": "accepted"}
