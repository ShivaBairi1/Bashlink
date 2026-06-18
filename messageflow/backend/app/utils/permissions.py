from typing import List
from fastapi import HTTPException, Depends, Request

def require_roles(allowed: List[str]):
    def _require(request: Request = None):
        user = getattr(request.state, 'user', None)
        if not user:
            raise HTTPException(status_code=401, detail='unauthorized')
        if user.get('role') not in allowed:
            raise HTTPException(status_code=403, detail='forbidden')
        return True
    return Depends(_require)
