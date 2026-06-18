import httpx
from app.core.config import settings
from typing import Dict, Any

class WhatsAppService:
    def __init__(self):
        self.base = settings.WHATSAPP_API_BASE
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN

    def _headers(self):
        return {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}

    def send_text_message(self, to_number: str, text: str) -> Dict[str, Any]:
        url = f"{self.base}/{self.phone_number_id}/messages"
        body = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": text}
        }
        r = httpx.post(url, json=body, headers=self._headers(), timeout=20)
        r.raise_for_status()
        return r.json()

    def send_template_message(self, to_number: str, template_name: str, components: list):
        url = f"{self.base}/{self.phone_number_id}/messages"
        body = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "en_US"},
                "components": components
            }
        }
        r = httpx.post(url, json=body, headers=self._headers(), timeout=20)
        r.raise_for_status()
        return r.json()

    def send_media_message(self, to_number: str, media_id: str, caption: str = ""):
        url = f"{self.base}/{self.phone_number_id}/messages"
        body = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "image",
            "image": {"id": media_id, "caption": caption}
        }
        r = httpx.post(url, json=body, headers=self._headers(), timeout=20)
        r.raise_for_status()
        return r.json()
