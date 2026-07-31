from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_roles
from app.models.user import User
from app.services.lab_pharmacy_service import lab_pharmacy_service
from app.repositories.lab_pharmacy_repository import medicine_repository, inventory_item_repository
from app.schemas.lab_pharmacy import (
    MedicineCreate, MedicineResponse, StockBatchCreate, StockBatchResponse,
    DispensingCreate, DispensingResponse, InventoryItemCreate, InventoryItemResponse
)
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/pharmacy", tags=["Pharmacy & Inventory Module"])

@router.post("/medicines", response_model=MedicineResponse, status_code=status.HTTP_201_CREATED)
def create_medicine(
    med_in: MedicineCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return lab_pharmacy_service.create_medicine(db, med_in)

@router.get("/medicines", response_model=PaginatedResponse[MedicineResponse])
def get_medicines(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items, total = medicine_repository.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)

@router.post("/stock-batches", response_model=StockBatchResponse, status_code=status.HTTP_201_CREATED)
def add_stock_batch(
    batch_in: StockBatchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return lab_pharmacy_service.add_stock_batch(db, batch_in)

@router.post("/validate-prescription/{prescription_id}")
def validate_prescription(
    prescription_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return lab_pharmacy_service.validate_prescription_before_dispensing(db, prescription_id)

@router.post("/dispense", response_model=DispensingResponse, status_code=status.HTTP_201_CREATED)
def dispense_medicine(
    disp_in: DispensingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return lab_pharmacy_service.dispense_medicine(db, disp_in)

@router.get("/alerts/expiry")
def expiry_alerts(
    days_ahead: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return lab_pharmacy_service.get_expiry_alerts(db, days_ahead)

@router.get("/alerts/low-stock")
def low_stock_alerts(
    threshold: int = Query(10, ge=0, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return lab_pharmacy_service.get_low_stock_alerts(db, threshold)

@router.post("/inventory", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
def create_inventory_item(
    inv_in: InventoryItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return lab_pharmacy_service.create_inventory_item(db, inv_in)

@router.get("/inventory", response_model=PaginatedResponse[InventoryItemResponse])
def get_inventory(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items, total = inventory_item_repository.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)
