from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserOut
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=dict)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    r = await svc.register(payload.company_name, payload.name, payload.email, payload.password)
    return {"company_id": r["company_id"], "user_id": r["user_id"]}

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    r = await svc.authenticate(payload.email, payload.password)
    if not r:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": r["access_token"], "refresh_token": r["refresh_token"]}

@router.get("/me", response_model=UserOut)
async def me(request = None):
    # example: request.state.user set by middleware
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return {"id": user["user_id"], "company_id": user["company_id"], "name": "", "email": "", "role": user["role"]}
