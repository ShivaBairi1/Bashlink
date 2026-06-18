@@
 @router.post('/{dlq_id}/retry', dependencies=[Depends(require_roles(["OWNER","ADMIN"]))])
 async def retry_dlq(dlq_id: str, db: AsyncSession = Depends(get_db), request: Request = None):
@@
     from app.workers.tasks import process_dlq_retry_task
     process_dlq_retry_task.delay({"dlq_id": dlq_id})
     return {"status": "enqueued"}
+
+
+@router.post('/batch_retry', dependencies=[Depends(require_roles(["OWNER","ADMIN"]))])
+async def batch_retry_dlq(ids: list[str], db: AsyncSession = Depends(get_db), request: Request = None):
+    user = getattr(request.state, 'user', None)
+    company_id = user['company_id']
+    q = select(models.ProviderFailedMessage).where(models.ProviderFailedMessage.id.in_(ids), models.ProviderFailedMessage.company_id == company_id)
+    res = await db.execute(q)
+    rows = res.scalars().all()
+    from app.workers.tasks import process_dlq_retry_task
+    for r in rows:
+        process_dlq_retry_task.delay({"dlq_id": r.id})
+    return {"status": "enqueued", "count": len(rows)}
