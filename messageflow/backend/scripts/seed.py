import asyncio
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.models import Company, User, Dataset, CustomerRecord
from app.utils.security import hash_password
import uuid
import pandas as pd

DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(DATABASE_URL, future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def seed():
    async with AsyncSessionLocal() as session:
        # create company
        company_id = str(uuid.uuid4())
        company = Company(id=company_id, company_name="ACME Corp", subscription_plan="starter", credits=1000)
        session.add(company)
        # create owner user
        user = User(id=str(uuid.uuid4()), company_id=company_id, name="Admin User", email="admin@acme.test", password_hash=hash_password("password"), role="OWNER")
        session.add(user)
        # create sample dataset
        dataset_id = str(uuid.uuid4())
        df = pd.DataFrame([{"Customer Name":"John Doe","Mobile":"+1234567890","Order Number":"ORD123","Collection Point":"London CP1"},
                           {"Customer Name":"Jane Smith","Mobile":"+1987654321","Order Number":"ORD456","Collection Point":"Manchester"}])
        column_map = [{"orig": c} for c in df.columns]
        dataset = Dataset(id=dataset_id, company_id=company_id, dataset_name="Sample Customers", uploaded_file_name="sample.csv", column_map=column_map)
        session.add(dataset)
        # insert customer records
        records = []
        for _, row in df.iterrows():
            records.append(CustomerRecord(id=str(uuid.uuid4()), company_id=company_id, dataset_id=dataset_id, phone=row.get("Mobile"), email=None, dynamic_fields=row.to_dict()))
        for r in records:
            session.add(r)
        await session.commit()
        print("Seeded company, user, dataset and customer records")

if __name__ == '__main__':
    asyncio.run(seed())
