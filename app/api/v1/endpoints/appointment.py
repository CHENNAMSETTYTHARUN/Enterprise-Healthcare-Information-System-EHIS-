from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.rbac import require_roles
from app.services.clinical_service import clinical_service
from app.schemas.clinical import AppointmentCreate, AppointmentResponse
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/appointments", tags=["Clinical - Appointments"])

@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN", "DOCTOR", "NURSE", "PATIENT"]))])
def schedule_appointment(appt_in: AppointmentCreate, db: Session = Depends(get_db)):
    """Schedule a new doctor consultation appointment."""
    return clinical_service.create_appointment(db, appt_in)

@router.get("", response_model=PaginatedResponse[AppointmentResponse])
def get_appointments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve scheduled appointments with filtering and pagination."""
    items, total = clinical_service.get_appointments(db, page=page, page_size=page_size, search=search)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)
