from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.rbac import require_roles
from app.services.clinical_service import clinical_service
from app.repositories.clinical_repository import opd_repository, ipd_repository
from app.schemas.clinical import OPDCreate, OPDResponse, IPDCreate, IPDResponse
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/clinical", tags=["Clinical - OPD & IPD"])

@router.post("/opd", response_model=OPDResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "DOCTOR", "NURSE"]))])
def create_opd_visit(opd_in: OPDCreate, db: Session = Depends(get_db)):
    """Record OPD outpatient visit."""
    return clinical_service.create_opd_record(db, opd_in)

@router.get("/opd", response_model=PaginatedResponse[OPDResponse])
def get_opd_visits(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    items, total = opd_repository.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)

@router.post("/ipd", response_model=IPDResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "DOCTOR", "NURSE"]))])
def create_ipd_admission(ipd_in: IPDCreate, db: Session = Depends(get_db)):
    """Admit patient to IPD inpatient ward."""
    return clinical_service.create_ipd_record(db, ipd_in)

@router.get("/ipd", response_model=PaginatedResponse[IPDResponse])
def get_ipd_admissions(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    items, total = ipd_repository.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)
