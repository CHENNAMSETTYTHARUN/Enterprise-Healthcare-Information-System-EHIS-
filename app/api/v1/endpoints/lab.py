from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.rbac import require_roles
from app.services.lab_pharmacy_service import lab_pharmacy_service
from app.repositories.lab_pharmacy_repository import lab_test_repository, lab_order_repository
from app.schemas.lab_pharmacy import (
    LabTestCreate, LabTestResponse, LabOrderCreate, LabOrderResponse,
    LabSampleCreate, LabSampleResponse, LabResultCreate, LabResultResponse
)
from app.schemas.common import PaginatedResponse
from app.background.tasks import process_lab_result_notification

router = APIRouter(prefix="/lab", tags=["Laboratory Module"])

@router.post("/tests", response_model=LabTestResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN", "LAB_TECH"]))])
def create_lab_test(test_in: LabTestCreate, db: Session = Depends(get_db)):
    """Define new laboratory test catalog item."""
    return lab_pharmacy_service.create_lab_test(db, test_in)

@router.get("/tests", response_model=PaginatedResponse[LabTestResponse])
def get_lab_tests(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    items, total = lab_test_repository.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)

@router.post("/orders", response_model=LabOrderResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "DOCTOR", "NURSE", "LAB_TECH"]))])
def create_lab_order(order_in: LabOrderCreate, db: Session = Depends(get_db)):
    """Order lab tests for a patient."""
    return lab_pharmacy_service.create_lab_order(db, order_in)

@router.get("/orders", response_model=PaginatedResponse[LabOrderResponse])
def get_lab_orders(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    items, total = lab_order_repository.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)

@router.post("/samples", response_model=LabSampleResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "LAB_TECH", "NURSE"]))])
def collect_sample(sample_in: LabSampleCreate, db: Session = Depends(get_db)):
    """Log sample collection with barcode."""
    return lab_pharmacy_service.collect_sample(db, sample_in)

@router.post("/results", response_model=LabResultResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "LAB_TECH"]))])
def publish_lab_result(result_in: LabResultCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Publish lab test result and notify patient/doctor."""
    res = lab_pharmacy_service.publish_result(db, result_in)
    background_tasks.add_task(process_lab_result_notification, res.lab_order_id, res.lab_test_id, res.result_value)
    return res
