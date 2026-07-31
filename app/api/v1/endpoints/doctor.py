from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.rbac import require_roles
from app.services.hospital_service import hospital_service, doctor_repo
from app.schemas.hospital import DoctorCreate, DoctorResponse
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/doctors", tags=["Hospital Management"])

@router.post("", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN"]))])
def create_doctor(doc_in: DoctorCreate, db: Session = Depends(get_db)):
    """Register doctor profile details."""
    return hospital_service.create_doctor(db, doc_in)

@router.get("", response_model=PaginatedResponse[DoctorResponse])
def get_doctors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve doctor list with specialization search and pagination."""
    items, total = doctor_repo.get_all(db, page=page, page_size=page_size, search=search, search_fields=["specialization", "license_number"])
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)
