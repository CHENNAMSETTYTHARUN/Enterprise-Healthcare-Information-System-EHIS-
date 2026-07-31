from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.rbac import require_roles
from app.services.hospital_service import hospital_service, department_repo
from app.schemas.hospital import DepartmentCreate, DepartmentResponse
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/departments", tags=["Hospital Management"])

@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN"]))])
def create_department(d_in: DepartmentCreate, db: Session = Depends(get_db)):
    """Create a new hospital department."""
    return hospital_service.create_department(db, d_in)

@router.get("", response_model=PaginatedResponse[DepartmentResponse])
def get_departments(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    items, total = department_repo.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)
