from fastapi import APIRouter, Request, HTTPException, status, Depends
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import models
from app.schemas.common import IDModel
from app.utils.security import decode_token
from sqlalchemy import select

router = APIRouter()

@router.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.json()
    # Validate signature if provided (not implemented here)
    # WhatsApp webhook payload contains 'entry' -> 'changes' with value -> 'messages' and 'metadata' including phone_number_id
    from app.workers.tasks import process_whatsapp_webhook_task
    # extract metadata
    entries = payload.get('entry', []) if isinstance(payload, dict) else []
    tasks = []
    for entry in entries:
        changes = entry.get('changes', [])
        for ch in changes:
            value = ch.get('value', {})
            metadata = value.get('metadata', {})
            phone_number_id = metadata.get('phone_number_id')
            messages = value.get('messages', [])
            for m in messages:
                task_payload = {
                    'phone_number_id': phone_number_id,
                    'message': m,
                    'raw': payload
                }
                process_whatsapp_webhook_task.delay(task_payload)
    return {"status": "accepted"}
