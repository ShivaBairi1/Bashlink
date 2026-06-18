from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class DatasetCreate(BaseModel):
    dataset_name: str

class DatasetOut(BaseModel):
    id: str
    dataset_name: str
    uploaded_file_name: Optional[str]
    column_map: Optional[Any]

class DatasetColumnsOut(BaseModel):
    columns: List[str]
