from pydantic import BaseModel
from typing import Optional

class CompanyCreate(BaseModel):
    company_name: str

class CompanyOut(BaseModel):
    id: str
    company_name: str
    subscription_plan: str
    credits: float
