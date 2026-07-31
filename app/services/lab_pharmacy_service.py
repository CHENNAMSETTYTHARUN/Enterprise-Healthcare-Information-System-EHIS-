from typing import List, Tuple, Optional
from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.lab_pharmacy_repository import (
    lab_test_repository, lab_order_repository, lab_sample_repository,
    lab_result_repository, medicine_repository, stock_batch_repository,
    dispensing_repository, inventory_item_repository
)
from app.schemas.lab_pharmacy import (
    LabTestCreate, LabOrderCreate, LabSampleCreate, LabResultCreate,
    MedicineCreate, StockBatchCreate, DispensingCreate, InventoryItemCreate
)
from app.models.lab_pharmacy import (
    LabTest, LabOrder, LabSample, LabResult, Medicine, StockBatch,
    MedicineDispensing, InventoryItem, LabOrderStatusEnum
)
from app.models.clinical import Prescription
from app.core.exceptions import NotFoundException

class LabPharmacyService:
    def create_lab_test(self, db: Session, test_in: LabTestCreate) -> LabTest:
        return lab_test_repository.create(db, test_in.model_dump())

    def create_lab_order(self, db: Session, order_in: LabOrderCreate) -> LabOrder:
        return lab_order_repository.create(db, order_in.model_dump())

    def collect_sample(self, db: Session, sample_in: LabSampleCreate) -> LabSample:
        sample = lab_sample_repository.create(db, sample_in.model_dump())
        order = lab_order_repository.get_by_id(db, sample_in.lab_order_id)
        if order:
            lab_order_repository.update(db, order, {"status": LabOrderStatusEnum.SAMPLE_COLLECTED})
        return sample

    def publish_result(self, db: Session, result_in: LabResultCreate) -> LabResult:
        result = lab_result_repository.create(db, result_in.model_dump())
        order = lab_order_repository.get_by_id(db, result_in.lab_order_id)
        if order:
            lab_order_repository.update(db, order, {"status": LabOrderStatusEnum.COMPLETED})
        return result

    def create_medicine(self, db: Session, med_in: MedicineCreate) -> Medicine:
        return medicine_repository.create(db, med_in.model_dump())

    def add_stock_batch(self, db: Session, batch_in: StockBatchCreate) -> StockBatch:
        return stock_batch_repository.create(db, batch_in.model_dump())

    def validate_prescription_before_dispensing(self, db: Session, prescription_id: str) -> dict:
        prescription = db.query(Prescription).filter(
            Prescription.id == prescription_id,
            Prescription.is_active == True
        ).first()

        if not prescription:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")

        issues = []

        for item in prescription.items:
            med = db.query(Medicine).filter(Medicine.id == item.medicine_id if hasattr(item, 'medicine_id') else None).first()
            if med:
                valid_batches = db.query(StockBatch).filter(
                    StockBatch.medicine_id == med.id,
                    StockBatch.expiry_date > date.today(),
                    StockBatch.quantity > 0,
                    StockBatch.is_active == True
                ).first()
                if not valid_batches:
                    issues.append(f"Medicine '{med.name}' is out of stock or all batches are expired")

        if issues:
            return {"valid": False, "issues": issues, "prescription_id": prescription_id}

        return {"valid": True, "issues": [], "prescription_id": prescription_id, "message": "Prescription is valid and medicines are available"}

    def dispense_medicine(self, db: Session, disp_in: DispensingCreate) -> MedicineDispensing:
        if disp_in.prescription_id:
            validation = self.validate_prescription_before_dispensing(db, disp_in.prescription_id)
            if not validation["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Prescription validation failed: {'; '.join(validation['issues'])}"
                )
        return dispensing_repository.create(db, disp_in.model_dump())

    def create_inventory_item(self, db: Session, inv_in: InventoryItemCreate) -> InventoryItem:
        return inventory_item_repository.create(db, inv_in.model_dump())

    def get_expiry_alerts(self, db: Session, days_ahead: int = 30):
        threshold = date.today()
        from datetime import timedelta
        threshold_future = threshold + timedelta(days=days_ahead)

        expired = db.query(StockBatch).filter(
            StockBatch.expiry_date < threshold,
            StockBatch.quantity > 0,
            StockBatch.is_active == True
        ).all()

        expiring_soon = db.query(StockBatch).filter(
            StockBatch.expiry_date >= threshold,
            StockBatch.expiry_date <= threshold_future,
            StockBatch.quantity > 0,
            StockBatch.is_active == True
        ).all()

        return {
            "days_ahead": days_ahead,
            "expired_count": len(expired),
            "expiring_soon_count": len(expiring_soon),
            "expired": [{"batch_number": b.batch_number, "medicine_id": b.medicine_id, "expiry_date": str(b.expiry_date), "quantity": b.quantity} for b in expired],
            "expiring_soon": [{"batch_number": b.batch_number, "medicine_id": b.medicine_id, "expiry_date": str(b.expiry_date), "quantity": b.quantity} for b in expiring_soon]
        }

    def get_low_stock_alerts(self, db: Session, threshold: int = 10):
        low_stock = db.query(StockBatch).filter(
            StockBatch.quantity <= threshold,
            StockBatch.quantity > 0,
            StockBatch.is_active == True
        ).all()

        out_of_stock = db.query(StockBatch).filter(
            StockBatch.quantity == 0,
            StockBatch.is_active == True
        ).all()

        return {
            "threshold": threshold,
            "low_stock_count": len(low_stock),
            "out_of_stock_count": len(out_of_stock),
            "low_stock": [{"batch_number": b.batch_number, "medicine_id": b.medicine_id, "quantity": b.quantity} for b in low_stock],
            "out_of_stock": [{"batch_number": b.batch_number, "medicine_id": b.medicine_id} for b in out_of_stock]
        }

lab_pharmacy_service = LabPharmacyService()
