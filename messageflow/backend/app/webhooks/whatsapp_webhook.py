from fastapi import APIRouter, Request
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.workers.tasks import process_whatsapp_webhook_task
from app.utils.phones import normalize_phone
from sqlalchemy import select
from app.models import models
import asyncio

router = APIRouter()

@router.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.json()
    entries = payload.get('entry', []) if isinstance(payload, dict) else []
    for entry in entries:
        changes = entry.get('changes', [])
        for ch in changes:
            value = ch.get('value', {})
            metadata = value.get('metadata', {})
            phone_number_id = metadata.get('phone_number_id')
            messages = value.get('messages', [])
            for m in messages:
                # normalize sender phone to help matching quickly in the webhook task
                from_number = m.get('from') or (m.get('wa_id') if isinstance(m, dict) else None)
                normalized = normalize_phone(from_number)
                task_payload = {
                    'phone_number_id': phone_number_id,
                    'message': m,
                    'normalized_from': normalized,
                    'raw': payload
                }
                process_whatsapp_webhook_task.delay(task_payload)
    return {"status": "accepted"}
