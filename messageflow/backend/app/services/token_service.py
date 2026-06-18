import redis.asyncio as aioredis
from datetime import timedelta
from app.core.config import settings

class TokenService:
    def __init__(self):
        self.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    async def store_refresh_token(self, token: str, user_id: str, expires_days: int):
        key = f"refresh:{token}"
        await self.redis.set(key, user_id, ex=timedelta(days=expires_days))

    async def revoke_refresh_token(self, token: str):
        key = f"refresh:{token}"
        await self.redis.delete(key)

    async def is_valid(self, token: str) -> bool:
        key = f"refresh:{token}"
        v = await self.redis.get(key)
        return v is not None

    async def get_user_id(self, token: str):
        key = f"refresh:{token}"
        return await self.redis.get(key)
