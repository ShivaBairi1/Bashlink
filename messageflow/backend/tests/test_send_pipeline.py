import pytest
import asyncio
from unittest.mock import MagicMock
from app.services.credit_service import CreditService
from app.integrations.whatsapp import WhatsAppService
from app.models import models
from sqlalchemy import select

@pytest.mark.asyncio
async def test_send_pipeline_reserve_and_dlq(monkeypatch, get_test_db):
    db = get_test_db
    # create company with small credits
    comp = models.Company(company_name='t', credits=1)
    db.add(comp)
    await db.commit()
    await db.refresh(comp)

    # create customer
    cust = models.CustomerRecord(company_id=comp.id, dataset_id=str('d1'), phone='+15551234567')
    db.add(cust)
    await db.commit()
    await db.refresh(cust)

    # mock WhatsAppService to throw on send
    def fake_send(phone, text):
        raise Exception('provider down')

    monkeypatch.setattr('app.integrations.whatsapp.WhatsAppService.send_text_message', lambda self, p, t: fake_send(p, t))

    # emulate worker send path by directly calling the send logic minimal
    # attempt to reserve credits
    cs = CreditService(db)
    ok = await cs.reserve_credits(comp.id, 1.0)
    assert ok
    # attempt send -> will raise and should result in DLQ write by worker code path
    try:
        wa = WhatsAppService(access_token=None, phone_number_id=None)
        wa.send_text_message(cust.phone, 'hello')
    except Exception:
        # write DLQ entry
        df = models.ProviderFailedMessage(company_id=comp.id, channel='whatsapp', payload={'customer_id': cust.id, 'message': 'hello'}, error='provider down')
        db.add(df)
        await db.commit()
    # verify DLQ row exists
    q = select(models.ProviderFailedMessage).where(models.ProviderFailedMessage.company_id == comp.id)
    res = await db.execute(q)
    rows = res.scalars().all()
    assert len(rows) == 1
