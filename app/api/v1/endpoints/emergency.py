from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.rbac import require_roles
from app.services.patient_service import patient_service
from app.repositories.patient_repository import emergency_repository, ambulance_repository
from app.schemas.patient import EmergencyCreate, EmergencyResponse, AmbulanceCreate, AmbulanceResponse
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/emergency", tags=["Emergency & Ambulance Management"])

@router.post("/triage", response_model=EmergencyResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN", "DOCTOR", "NURSE"]))])
def create_emergency_triage(emergency_in: EmergencyCreate, db: Session = Depends(get_db)):
    """Create emergency room triage record."""
    return patient_service.create_emergency(db, emergency_in)

@router.get("/triage", response_model=PaginatedResponse[EmergencyResponse], dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN", "DOCTOR", "NURSE"]))])
def get_emergencies(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    items, total = emergency_repository.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)

@router.post("/ambulances", response_model=AmbulanceResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN"]))])
def register_ambulance(amb_in: AmbulanceCreate, db: Session = Depends(get_db)):
    return patient_service.create_ambulance(db, amb_in)

@router.get("/ambulances", response_model=PaginatedResponse[AmbulanceResponse])
def get_ambulances(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    items, total = ambulance_repository.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)
