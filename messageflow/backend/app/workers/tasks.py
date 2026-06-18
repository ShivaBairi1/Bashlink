from .celery_app import celery
from app.core.config import settings
import asyncio
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models import models
from app.services.variable_resolver import VariableResolver
from sqlalchemy import select, update, insert
import json
import os

DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(DATABASE_URL, future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@celery.task(bind=True, soft_time_limit=600)
def bulk_send_campaign_task(company_id: str, campaign_id: str):
    """
    Celery worker task: generate messages for campaign and send them via provider abstraction.
    This runs in a worker container. It's synchronous (Celery), but uses async SQLAlchemy via asyncio loop.
    """
    asyncio.run(_bulk_send_campaign(company_id, campaign_id))

async def _bulk_send_campaign(company_id: str, campaign_id: str):
    async with AsyncSessionLocal() as session:
        # load campaign, template, dataset
        q = select(models.Campaign).where(models.Campaign.id == campaign_id)
        res = await session.execute(q)
        campaign = res.scalar_one_or_none()
        if not campaign:
            return
        tmpl_q = select(models.Template).where(models.Template.id == campaign.template_id)
        tmpl = (await session.execute(tmpl_q)).scalar_one_or_none()
        # fetch customers in batches
        offset = 0
        batch = 500
        while True:
            q = select(models.CustomerRecord).where(models.CustomerRecord.company_id == company_id, models.CustomerRecord.dataset_id == campaign.dataset_id).limit(batch).offset(offset)
            res = await session.execute(q)
            rows = res.scalars().all()
            if not rows:
                break
            msgs = []
            for r in rows:
                text = VariableResolver.render(tmpl.template_content, r.dynamic_fields, fallback="")
                msg = {
                    "id": r.id + "-" + campaign.id,  # not ideal, but unique-ish; prefer uuid
                    "company_id": company_id,
                    "campaign_id": campaign_id,
                    "customer_record_id": r.id,
                    "channel": tmpl.channel,
                    "generated_message": text,
                    "status": "queued"
                }
                # create a Message row
                # using sqlalchemy core insert per-row is slow; use many-insert below
                msgs.append({
                    "id": str(os.urandom(16).hex()),
                    "company_id": company_id,
                    "campaign_id": campaign_id,
                    "customer_record_id": r.id,
                    "channel": tmpl.channel,
                    "generated_message": text,
                    "status": "queued"
                })
            if msgs:
                await session.execute(insert(models.Message).values(msgs))
                await session.commit()
            offset += batch
        # Enqueue send jobs per-message or chunk them; for example here we will just mark campaign queued
        await session.execute(update(models.Campaign).where(models.Campaign.id == campaign_id).values(status="queued"))
        await session.commit()

@celery.task(bind=True)
def process_whatsapp_webhook_task(payload: dict):
    # process incoming webhook: create Reply rows etc.
    asyncio.run(_process_whatsapp_webhook(payload))

async def _process_whatsapp_webhook(payload: dict):
    # This is provider-specific; implement mapping to replies/messages
    async with AsyncSessionLocal() as session:
        # For each message in payload, create Reply row and attempt to map to customer record by phone
        # Simplified example:
        contacts = payload.get("contacts") or []
        messages = payload.get("messages") or []
        for m in messages:
            phone = m.get("from")
            text = m.get("text", {}).get("body") if isinstance(m.get("text"), dict) else m.get("text")
            # find customer
            q = select(models.CustomerRecord).where(models.CustomerRecord.company_id == None)  # placeholder
            # In production implement proper matching
            # Create reply row (company_id and mapping should be derived from webhook)
            r = models.Reply(id=str(os.urandom(16).hex()), company_id=None, customer_record_id=None, message_text=text, provider_event=payload)
            session.add(r)
        await session.commit()

@celery.task(bind=True)
def process_excel_import_task(company_id: str, dataset_id: str, s3_path: str):
    # download from S3 and process - omitted here for brevity
    return True
