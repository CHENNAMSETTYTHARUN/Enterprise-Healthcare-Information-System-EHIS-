from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.rbac import require_roles
from app.services.clinical_service import clinical_service
from app.repositories.clinical_repository import (
    emr_repository, diagnosis_repository, treatment_plan_repository,
    prescription_repository, clinical_note_repository
)
from app.schemas.clinical import (
    EMRCreate, EMRResponse, DiagnosisCreate, DiagnosisResponse,
    TreatmentPlanCreate, TreatmentPlanResponse, PrescriptionCreate, PrescriptionResponse,
    ClinicalNoteCreate, ClinicalNoteResponse
)
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/emr", tags=["Clinical - EMR & Prescriptions"])

@router.post("/records", response_model=EMRResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "DOCTOR"]))])
def create_emr_entry(emr_in: EMRCreate, db: Session = Depends(get_db)):
    """Create Electronic Medical Record (EMR) entry."""
    return clinical_service.create_emr_record(db, emr_in)

@router.get("/records", response_model=PaginatedResponse[EMRResponse])
def get_emr_records(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    items, total = emr_repository.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)

@router.post("/diagnoses", response_model=DiagnosisResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "DOCTOR"]))])
def create_diagnosis(diag_in: DiagnosisCreate, db: Session = Depends(get_db)):
    return clinical_service.create_diagnosis(db, diag_in)

@router.post("/treatment-plans", response_model=TreatmentPlanResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "DOCTOR"]))])
def create_treatment_plan(tp_in: TreatmentPlanCreate, db: Session = Depends(get_db)):
    return clinical_service.create_treatment_plan(db, tp_in)

@router.post("/prescriptions", response_model=PrescriptionResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "DOCTOR"]))])
def create_prescription(presc_in: PrescriptionCreate, db: Session = Depends(get_db)):
    """Issue digital prescription with multi-item medicines."""
    return clinical_service.create_prescription(db, presc_in)

@router.get("/prescriptions", response_model=PaginatedResponse[PrescriptionResponse])
def get_prescriptions(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    items, total = prescription_repository.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)

@router.post("/notes", response_model=ClinicalNoteResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "DOCTOR", "NURSE"]))])
def create_clinical_note(note_in: ClinicalNoteCreate, db: Session = Depends(get_db)):
    return clinical_service.create_clinical_note(db, note_in)
