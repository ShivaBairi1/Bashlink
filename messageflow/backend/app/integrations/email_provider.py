import aiosmtplib
from email.message import EmailMessage
from app.core.config import settings
from typing import List, Dict, Any

class EmailService:
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_addr = settings.EMAIL_FROM

    async def send_email(self, to_email: str, subject: str, html_body: str, text_body: str | None = None):
        msg = EmailMessage()
        msg["From"] = self.from_addr
        msg["To"] = to_email
        msg["Subject"] = subject
        if text_body:
            msg.set_content(text_body)
            msg.add_alternative(html_body, subtype="html")
        else:
            msg.set_content(html_body, subtype="html")
        await aiosmtplib.send(msg, hostname=self.host, port=self.port, username=self.user, password=self.password, start_tls=True)
        return True

    async def send_bulk_email(self, recipients: List[Dict[str, str]], subject: str, html_template: str):
        # naive implementation; in production use SES/SendGrid/Bulk API
        for r in recipients:
            await self.send_email(r['email'], subject, html_template, text_body=None)
        return True
