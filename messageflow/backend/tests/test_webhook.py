diff --git a/messageflow/backend/tests/test_webhook.py b/messageflow/backend/tests/test_webhook.py
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/messageflow/backend/tests/test_webhook.py
@@
+import pytest
+from httpx import AsyncClient
+from app.main import app
+
+
+@pytest.mark.asyncio
+async def test_whatsapp_webhook_enqueue():
+    payload = {
+        "entry": [
+            {"changes": [{"value": {"metadata": {"phone_number_id": "12345"}, "messages": [{"from": "+1234567890", "text": {"body": "hello"}}]}}]}
+        ]
+    }
+    async with AsyncClient(app=app, base_url="http://test") as client:
+        res = await client.post('/webhooks/whatsapp', json=payload)
+        assert res.status_code == 200
+        assert res.json().get('status') == 'accepted'
+