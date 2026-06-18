from fastapi import Request
from app.utils.security import decode_token
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Attempt to extract bearer token and set request.state.company_id and user info
        auth = request.headers.get("Authorization")
        request.state.user = None
        request.state.company_id = None
        if auth and auth.startswith("Bearer "):
            token = auth.split(" ", 1)[1]
            try:
                payload = decode_token(token)
                request.state.user = {
                    "user_id": payload.get("sub"),
                    "company_id": payload.get("company_id"),
                    "role": payload.get("role")
                }
                request.state.company_id = payload.get("company_id")
            except Exception:
                # invalid token - leave user None
                pass
        response = await call_next(request)
        return response
