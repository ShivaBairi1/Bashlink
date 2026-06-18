from pydantic import BaseModel
from typing import Optional, List

class TemplateCreate(BaseModel):
    template_name: str
    channel: str
    template_content: str

class TemplateOut(BaseModel):
    id: str
    template_name: str
    channel: str
    template_content: str
    status: str
