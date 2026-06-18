@@
 from app.integrations.whatsapp import WhatsAppService
 from app.integrations.email_provider import EmailService
 from app.services.credit_service import CreditService
 from app.utils.idempotency import make_idempotency_key
 from sqlalchemy.exc import IntegrityError
+from app.utils.limiter import RedisLimiter
@@
-                # respect per-company rate limit if configured
-                rate_limit = None
-                try:
-                    wq = select(models.WhatsAppConfig).where(models.WhatsAppConfig.company_id == company_id)
-                    wres = await session.execute(wq)
-                    wconf = wres.scalar_one_or_none()
-                    rate_limit = getattr(wconf, 'rate_limit', None) if wconf else None
-                except Exception:
-                    wconf = None
+                # respect per-company rate limit and concurrency if configured
+                rate_limit = None
+                concurrency = None
+                try:
+                    wq = select(models.WhatsAppConfig).where(models.WhatsAppConfig.company_id == company_id)
+                    wres = await session.execute(wq)
+                    wconf = wres.scalar_one_or_none()
+                    rate_limit = getattr(wconf, 'rate_limit', None) if wconf else None
+                    concurrency = getattr(wconf, 'concurrency', None) if wconf else None
+                except Exception:
+                    wconf = None
+
+                limiter = RedisLimiter(redis_url=None)
@@
-                for attempt in range(3):
+                for attempt in range(3):
                     try:
+                        # acquire concurrency slot if configured
+                        if concurrency and int(concurrency) > 0:
+                            ok = limiter.acquire(company_id, int(concurrency), wait_seconds=2, timeout=30)
+                            if not ok:
+                                # couldn't acquire slot quickly - back off and retry
+                                await asyncio.sleep(0.5)
+                                continue
                         if tmpl.channel == 'whatsapp':
-                            wa = WhatsAppService(access_token=(wconf.access_token if wconf else None), phone_number_id=(wconf.phone_number_id if wconf else None))
-                            res = wa.send_text_message(r.phone, text)
+                            wa = WhatsAppService(access_token=(wconf.access_token if wconf else None), phone_number_id=(wconf.phone_number_id if wconf else None))
+                            res = wa.send_text_message(r.phone, text)
@@
-                            await session.commit()
-                            sent = True
-                            break
+                            await session.commit()
+                            sent = True
+                            break
@@
-                if rate_limit and rate_limit > 0:
-                    await asyncio.sleep(1.0 / float(rate_limit))
+                if rate_limit and rate_limit > 0:
+                    await asyncio.sleep(1.0 / float(rate_limit))
+
+                # release concurrency slot if acquired
+                try:
+                    if concurrency and int(concurrency) > 0:
+                        limiter.release(company_id)
+                except Exception:
+                    pass
+
+                if not sent:
