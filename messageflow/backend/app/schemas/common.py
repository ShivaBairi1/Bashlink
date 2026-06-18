from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime

class Meta(BaseModel):
    created_at: Optional[datetime]

class IDModel(BaseModel):
    id: str

class Paginated(BaseModel):
    total: int = 0
    items: List[Any] = []
