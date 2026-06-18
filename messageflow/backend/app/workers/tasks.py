@@
 @celery.task(bind=True)
 def process_whatsapp_webhook_task(self, payload: dict):
@@
     async def _process_whatsapp_webhook(payload: dict):
@@
         # insert reply
         reply = models.Reply(id=str(os.urandom(16).hex()), company_id=company_id, customer_record_id=customer_id, message_text=text, provider_event=payload)
         session.add(reply)
         await session.commit()
+
+
+@celery.task(bind=True)
+def process_dlq_retry_task(self, payload: dict):
+    return asyncio.run(_process_dlq_retry(payload))
+
+
+async def _process_dlq_retry(payload: dict):
+    async with AsyncSessionLocal() as session:
+        dlq_id = payload.get('dlq_id')
+        q = select(models.ProviderFailedMessage).where(models.ProviderFailedMessage.id == dlq_id)
+        res = await session.execute(q)
+        entry = res.scalar_one_or_none()
+        if not entry:
+            return False
+        # naive retry: attempt to re-send based on payload
+        channel = entry.channel
+        p = entry.payload or {}
+        company_id = entry.company_id
+        # find message or reconstruct
+        msg_text = p.get('message') or p.get('generated_message') or ''
+        cust_id = p.get('customer_id')
+        # perform send similar to bulk_send logic but minimal
+        try:
+            if channel == 'whatsapp':
+                wq = select(models.WhatsAppConfig).where(models.WhatsAppConfig.company_id == company_id)
+                wres = await session.execute(wq)
+                wconf = wres.scalar_one_or_none()
+                wa = WhatsAppService(access_token=(wconf.access_token if wconf else None), phone_number_id=(wconf.phone_number_id if wconf else None))
+                # find customer phone
+                cust = None
+                if cust_id:
+                    cq = select(models.CustomerRecord).where(models.CustomerRecord.id == cust_id)
+                    cres = await session.execute(cq)
+                    cust = cres.scalar_one_or_none()
+                if not cust:
+                    return False
+                res = wa.send_text_message(cust.phone or '', msg_text)
+                provider_id = None
+                try:
+                    provider_id = res.get('messages', [])[0].get('id') if isinstance(res, dict) and res.get('messages') else None
+                except Exception:
+                    provider_id = None
+                # update original message if present
+                if entry.message_id:
+                    await session.execute(update(models.Message).where(models.Message.id == entry.message_id).values(status='sent', provider_message_id=provider_id))
+                # delete DLQ entry
+                await session.execute(delete(models.ProviderFailedMessage).where(models.ProviderFailedMessage.id == dlq_id))
+                await session.commit()
+                return True
+        except Exception:
+            # leave DLQ entry for manual retry
+            return False
