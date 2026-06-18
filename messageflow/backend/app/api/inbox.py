from fastapi import APIRouter, Depends, Request, HTTPException
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import models
import uuid

router = APIRouter(prefix="/inbox", tags=["inbox"])

@router.get("/")
async def get_inbox(request: Request, db: AsyncSession = Depends(get_db)):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401)
    q = select(models.Message).where(models.Message.company_id == user["company_id"]).order_by(models.Message.created_at.desc()).limit(200)
    res = await db.execute(q)
    msgs = res.scalars().all()
    return [{"id": m.id, "customer_record_id": m.customer_record_id, "generated_message": m.generated_message, "status": m.status, "created_at": m.created_at} for m in msgs]

@router.get("/conversations/{customer_id}")
async def get_conversation(customer_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401)
    q = select(models.Message).where(models.Message.company_id == user["company_id"], models.Message.customer_record_id == customer_id).order_by(models.Message.created_at.asc())
    res = await db.execute(q)
    msgs = res.scalars().all()
    q2 = select(models.Reply).where(models.Reply.company_id == user["company_id"], models.Reply.customer_record_id == customer_id).order_by(models.Reply.received_at.asc())
    res2 = await db.execute(q2)
    replies = res2.scalars().all()
    items = []
    for m in msgs:
        items.append({"type": "outgoing", "text": m.generated_message, "created_at": m.created_at})
    for r in replies:
        items.append({"type": "incoming", "text": r.message_text, "created_at": r.received_at})
    items_sorted = sorted(items, key=lambda x: x["created_at"]) if items else []
    return items_sorted

@router.post("/reply")
async def reply_to_customer(customer_id: str, message_text: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401)
    # create reply row
    from app.models.models import Reply
    r = Reply(id=str(uuid.uuid4()), company_id=user["company_id"], customer_record_id=customer_id, message_text=message_text)
    db.add(r)
    await db.commit()
    return {"status": "ok"}
