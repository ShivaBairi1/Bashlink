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
from app.integrations.whatsapp import WhatsAppService
from app.integrations.email_provider import EmailService
from app.services.credit_service import CreditService

DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(DATABASE_URL, future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@celery.task(bind=True, soft_time_limit=600)
def bulk_send_campaign_task(self, company_id: str, campaign_id: str):
    """
    Celery worker task: generate messages for campaign and send them via provider abstraction.
    This runs in a worker container. It's synchronous (Celery), but uses async SQLAlchemy via asyncio loop.
    """
    return asyncio.run(_bulk_send_campaign(company_id, campaign_id))

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
        # fetch customers in batches and send messages immediately
        offset = 0
        batch = 200
        whatsapp_service = WhatsAppService()
        email_service = EmailService()
        credit_svc = CreditService(session, company_id)
        while True:
            q = select(models.CustomerRecord).where(models.CustomerRecord.company_id == company_id, models.CustomerRecord.dataset_id == campaign.dataset_id).limit(batch).offset(offset)
            res = await session.execute(q)
            rows = res.scalars().all()
            if not rows:
                break

            for r in rows:
                # render message
                text = VariableResolver.render(tmpl.template_content, r.dynamic_fields, fallback="")
                # create message record
                msg_id = str(os.urandom(16).hex())
                await session.execute(insert(models.Message).values({
                    "id": msg_id,
                    "company_id": company_id,
                    "campaign_id": campaign_id,
                    "customer_record_id": r.id,
                    "channel": tmpl.channel,
                    "generated_message": text,
                    "status": "sending"
                }))
                await session.commit()

                # determine cost
                cost = 1.0 if tmpl.channel == 'whatsapp' else 0.5

                try:
                    # reserve credits atomically
                    await credit_svc.consume_credits_atomic(cost)
                except Exception as e:
                    # insufficient credits -> mark message failed and record
                    await session.execute(update(models.Message).where(models.Message.id == msg_id).values(status='failed'))
                    await session.execute(insert(models.ProviderFailedMessage).values({
                        'id': str(os.urandom(16).hex()),
                        'company_id': company_id,
                        'message_id': msg_id,
                        'channel': tmpl.channel,
                        'payload': {'reason': 'insufficient_credits'},
                        'error': str(e)
                    }))
                    await session.commit()
                    continue

                # send via provider with simple retry
                sent = False
                last_error = None
                for attempt in range(3):
                    try:
                        if tmpl.channel == 'whatsapp':
                            # lookup whatsapp config for this company
                            wq = select(models.WhatsAppConfig).where(models.WhatsAppConfig.company_id == company_id)
                            wres = await session.execute(wq)
                            wconf = wres.scalar_one_or_none()
                            wa = WhatsAppService(access_token=(wconf.access_token if wconf else None), phone_number_id=(wconf.phone_number_id if wconf else None))
                            res = wa.send_text_message(r.phone, text)
                            provider_id = None
                            try:
                                provider_id = res.get('messages', [])[0].get('id') if isinstance(res, dict) and res.get('messages') else None
                            except Exception:
                                provider_id = None
                            await session.execute(update(models.Message).where(models.Message.id == msg_id).values(status='sent', provider_message_id=provider_id))
                            await session.commit()
                            sent = True
                            break
                        else:
                            # email send
                            await email_service.send_email(r.email or '', 'MessageFlow', text)
                            await session.execute(update(models.Message).where(models.Message.id == msg_id).values(status='sent'))
                            await session.commit()
                            sent = True
                            break
                    except Exception as e:
                        last_error = str(e)
                        await asyncio.sleep(2 ** attempt)

                if not sent:
                    # push to DLQ table
                    await session.execute(update(models.Message).where(models.Message.id == msg_id).values(status='failed'))
                    await session.execute(insert(models.ProviderFailedMessage).values({
                        'id': str(os.urandom(16).hex()),
                        'company_id': company_id,
                        'message_id': msg_id,
                        'channel': tmpl.channel,
                        'payload': {'customer_id': r.id, 'message': text},
                        'error': last_error
                    }))
                    # refund credits on failure
                    await credit_svc.add_credits(cost)
                    await session.commit()
            offset += batch

        # mark campaign completed
        await session.execute(update(models.Campaign).where(models.Campaign.id == campaign_id).values(status="completed"))
        await session.commit()

@celery.task(bind=True)
def process_whatsapp_webhook_task(self, payload: dict):
    # process incoming webhook: create Reply rows etc.
    return asyncio.run(_process_whatsapp_webhook(payload))

async def _process_whatsapp_webhook(payload: dict):
    # This is provider-specific; implement mapping to replies/messages
    async with AsyncSessionLocal() as session:
        # Expected payload: {'phone_number_id':..., 'message': { ... }, 'raw': ...}
        phone_number_id = payload.get('phone_number_id')
        message = payload.get('message')
        if not message:
            return
        # map phone_number_id to company via whatsapp_configs
        q = select(models.WhatsAppConfig).where(models.WhatsAppConfig.phone_number_id == phone_number_id)
        res = await session.execute(q)
        wconf = res.scalar_one_or_none()
        company_id = wconf.company_id if wconf else None
        # extract from and text
        from_number = message.get('from') or message.get('from_me') or (message.get('wa_id') if isinstance(message, dict) else None)
        text = None
        if isinstance(message.get('text'), dict):
            text = message.get('text').get('body')
        else:
            text = message.get('text')
        # normalize phone
        if not from_number:
            return
        # find customer by phone within company
        cust_q = select(models.CustomerRecord).where(models.CustomerRecord.dynamic_fields['Mobile'].astext == from_number) if company_id else select(models.CustomerRecord).where(models.CustomerRecord.dynamic_fields['Mobile'].astext == from_number)
        cust_res = await session.execute(cust_q)
        cust = cust_res.scalar_one_or_none()
        customer_id = cust.id if cust else None
        # insert reply
        reply = models.Reply(id=str(os.urandom(16).hex()), company_id=company_id, customer_record_id=customer_id, message_text=text, provider_event=payload)
        session.add(reply)
        await session.commit()

@celery.task(bind=True)
def process_excel_import_task(self, company_id: str, dataset_id: str, s3_path: str):
    # download from S3 and process - omitted here for brevity
    return True
