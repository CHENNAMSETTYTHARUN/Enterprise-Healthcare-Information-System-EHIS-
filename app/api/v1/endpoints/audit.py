from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.rbac import require_roles
from app.repositories.base import BaseRepository
from app.models.audit import AuditLog
from app.schemas.common import PaginatedResponse
from pydantic import BaseModel
from datetime import datetime

audit_repo = BaseRepository[AuditLog](AuditLog)

class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    action: str
    endpoint: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

router = APIRouter(prefix="/audit", tags=["Enterprise Services"])

@router.get("/logs", response_model=PaginatedResponse[AuditLogResponse], dependencies=[Depends(require_roles(["SUPER_ADMIN"]))])
def get_audit_logs(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    """Retrieve system security audit trails."""
    items, total = audit_repo.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)
