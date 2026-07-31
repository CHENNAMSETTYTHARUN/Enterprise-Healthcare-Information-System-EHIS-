from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.rbac import require_roles
from app.services.hospital_service import hospital_service
from app.schemas.hospital import HospitalCreate, HospitalResponse
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/hospitals", tags=["Hospital Management"])

@router.post("", response_model=HospitalResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN"]))])
def create_hospital(h_in: HospitalCreate, db: Session = Depends(get_db)):
    """Create a new hospital entry."""
    return hospital_service.create_hospital(db, h_in)

@router.get("", response_model=PaginatedResponse[HospitalResponse])
def get_hospitals(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve all hospitals with pagination and search."""
    items, total = hospital_service.get_all_hospitals(db, page=page, page_size=page_size, search=search)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)
