from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.rbac import require_roles
from app.services.patient_service import patient_service
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from app.schemas.common import PaginatedResponse, GenericResponse

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN", "DOCTOR", "NURSE"]))])
def create_patient(patient_in: PatientCreate, db: Session = Depends(get_db)):
    return patient_service.create_patient(db, patient_in)

@router.get("", response_model=PaginatedResponse[PatientResponse], dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN", "DOCTOR", "NURSE", "ACCOUNTANT"]))])
def get_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = "created_at",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    items, total = patient_service.get_all_patients(db, page=page, page_size=page_size, search=search, sort_by=sort_by, sort_order=sort_order)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)

@router.get("/{patient_id}", response_model=PatientResponse, dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN", "DOCTOR", "NURSE", "PATIENT"]))])
def get_patient_by_id(patient_id: str, db: Session = Depends(get_db)):
    return patient_service.get_patient(db, patient_id)

@router.put("/{patient_id}", response_model=PatientResponse, dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN", "DOCTOR"]))])
def update_patient(patient_id: str, patient_in: PatientUpdate, db: Session = Depends(get_db)):
    return patient_service.update_patient(db, patient_id, patient_in)

@router.delete("/{patient_id}", response_model=GenericResponse, dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN"]))])
def delete_patient(patient_id: str, db: Session = Depends(get_db)):
    patient_service.delete_patient(db, patient_id)
    return GenericResponse(message=f"Patient '{patient_id}' record deactivated.")
