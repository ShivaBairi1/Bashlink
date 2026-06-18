from app.repositories.users import UserRepository
from app.models.models import User, Company
from app.utils.security import hash_password, verify_password, create_access_token, decode_token
from app.core.config import settings
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import AsyncSessionLocal
import uuid
from sqlalchemy import insert, select
from app.models.models import Company as CompanyModel
from app.services.token_service import TokenService

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_service = TokenService()

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
        # store refresh token in redis for revocation
        await self.token_service.store_refresh_token(refresh_token, str(user.id), settings.REFRESH_TOKEN_EXPIRE_DAYS)
        return {"access_token": access_token, "refresh_token": refresh_token, "user": user}

    async def refresh(self, refresh_token: str):
        try:
            payload = decode_token(refresh_token)
        except Exception:
            return None
        # verify stored
        valid = await self.token_service.is_valid(refresh_token)
        if not valid:
            return None
        user_id = await self.token_service.get_user_id(refresh_token)
        # issue new tokens
        q = select(User).where(User.id == user_id)
        res = await self.db.execute(q)
        user = res.scalar_one_or_none()
        if not user:
            return None
        access_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        token_data = {"sub": str(user.id), "company_id": str(user.company_id), "role": user.role}
        access_token = create_access_token(token_data, expires_delta=access_expires)
        new_refresh_token = create_access_token(token_data, expires_delta=refresh_expires)
        # rotate: revoke old and store new
        await self.token_service.revoke_refresh_token(refresh_token)
        await self.token_service.store_refresh_token(new_refresh_token, str(user.id), settings.REFRESH_TOKEN_EXPIRE_DAYS)
        return {"access_token": access_token, "refresh_token": new_refresh_token, "user": user}

    async def logout(self, refresh_token: str):
        await self.token_service.revoke_refresh_token(refresh_token)
        return True
