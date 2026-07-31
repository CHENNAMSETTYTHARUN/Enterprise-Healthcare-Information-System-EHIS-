from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.rbac import require_roles
from app.services.clinical_service import clinical_service
from app.repositories.clinical_repository import surgery_repository, discharge_summary_repository
from app.schemas.clinical import SurgeryCreate, SurgeryResponse, DischargeSummaryCreate, DischargeSummaryResponse
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/surgeries", tags=["Clinical - Surgeries & Discharge"])

@router.post("", response_model=SurgeryResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "DOCTOR"]))])
def schedule_surgery(surgery_in: SurgeryCreate, db: Session = Depends(get_db)):
    """Schedule surgical operation."""
    return clinical_service.create_surgery(db, surgery_in)

@router.get("", response_model=PaginatedResponse[SurgeryResponse])
def get_surgeries(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    items, total = surgery_repository.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)

@router.post("/discharge-summaries", response_model=DischargeSummaryResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "DOCTOR"]))])
def generate_discharge_summary(ds_in: DischargeSummaryCreate, db: Session = Depends(get_db)):
    """Generate patient discharge summary and auto-release IPD bed."""
    return clinical_service.create_discharge_summary(db, ds_in)
