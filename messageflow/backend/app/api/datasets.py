from fastapi import APIRouter, Depends, Request, HTTPException
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.dataset_service import DatasetService
from app.schemas.dataset import DatasetCreate, DatasetOut, DatasetColumnsOut
from fastapi import Request
from app.utils.permissions import require_roles

router = APIRouter(prefix="/datasets", tags=["datasets"])

@router.post("/upload", response_model=DatasetOut)
async def upload_dataset(request: Request, file: UploadFile = File(...), dataset_name: str | None = None, db: AsyncSession = Depends(get_db), _=require_roles(["OWNER","MANAGER","ADMIN"])):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="unauthorized")
    company_id = user["company_id"]
    content = await file.read()
    svc = DatasetService(db, company_id)
    ds = await svc.create_dataset_from_file(dataset_name or file.filename, content, file.filename)
    return {"id": ds.id, "dataset_name": ds.dataset_name, "uploaded_file_name": ds.uploaded_file_name, "column_map": ds.column_map}
