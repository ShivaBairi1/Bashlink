import csv
import io
from typing import List, Dict, Any
from app.repositories.datasets import DatasetRepository
from app.models.models import Dataset, CustomerRecord
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import security
import pandas as pd
import uuid

class DatasetService:
    def __init__(self, db: AsyncSession, company_id: str):
        self.db = db
        self.repo = DatasetRepository(db, company_id=company_id)
        self.company_id = company_id

    async def create_dataset_from_file(self, dataset_name: str, file_bytes: bytes, filename: str):
        # detect type by extension and parse
        df = None
        if filename.lower().endswith((".xls", ".xlsx")):
            df = pd.read_excel(io.BytesIO(file_bytes), dtype=str)
        else:
            # CSV, detect encoding and parse
            s = io.StringIO(file_bytes.decode('utf-8', errors='replace'))
            df = pd.read_csv(s, dtype=str)
        df = df.fillna("")
        columns = list(df.columns)
        column_map = [{"orig": c} for c in columns]
        dataset = Dataset(id=str(uuid.uuid4()), company_id=self.company_id, dataset_name=dataset_name, uploaded_file_name=filename, column_map=column_map)
        await self.repo.create(dataset)
        # bulk insert customer records
        records = []
        for _, row in df.iterrows():
            dynamic = {c: (row.get(c) if row.get(c) is not None else "") for c in columns}
            rec = {
                "id": str(uuid.uuid4()),
                "company_id": self.company_id,
                "dataset_id": dataset.id,
                "phone": dynamic.get("phone") or dynamic.get("Phone") or None,
                "email": dynamic.get("email") or dynamic.get("Email") or None,
                "dynamic_fields": dynamic
            }
            records.append(rec)
            if len(records) >= 5000:
                await self.repo.bulk_insert_records(records)
                records = []
        if records:
            await self.repo.bulk_insert_records(records)
        await self.db.commit()
        return dataset

    async def get_columns(self, dataset_id: str) -> List[str]:
        d = await self.repo.get(dataset_id)
        if not d:
            return []
        cols = [c.get("orig") if isinstance(c, dict) else c for c in (d.column_map or [])]
        return cols
