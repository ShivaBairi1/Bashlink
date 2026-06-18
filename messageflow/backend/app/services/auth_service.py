from app.repositories.users import UserRepository
from app.models.models import User, Company
from app.utils.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import AsyncSessionLocal
import uuid
from sqlalchemy import insert, select
from app.models.models import Company as CompanyModel

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, company_name: str, name: str, email: str, password: str):
        # create company and owner user in a transaction
        company_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        stmt = insert(CompanyModel).values(id=company_id, company_name=company_name, subscription_plan="starter")
        await self.db.execute(stmt)
        stmt_user = insert(User).values(id=user_id, company_id=company_id, name=name, email=email, password_hash=hash_password(password), role="OWNER")
        await self.db.execute(stmt_user)
        await self.db.commit()
        return {"company_id": company_id, "user_id": user_id}

    async def authenticate(self, email: str, password: str):
        q = select(User).where(User.email == email)
        res = await self.db.execute(q)
        user = res.scalar_one_or_none()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        # create tokens
        access_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        token_data = {"sub": str(user.id), "company_id": str(user.company_id), "role": user.role}
        access_token = create_access_token(token_data, expires_delta=access_expires)
        refresh_token = create_access_token(token_data, expires_delta=refresh_expires)  # for simplicity store as JWT
        return {"access_token": access_token, "refresh_token": refresh_token, "user": user}
