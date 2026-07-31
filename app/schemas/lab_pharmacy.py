from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, Field
from app.models.lab_pharmacy import LabOrderStatusEnum

class LabTestCreate(BaseModel):
    code: str = Field(..., example="CBC-001")
    name: str = Field(..., example="Complete Blood Count")
    category: Optional[str] = Field(None, example="Hematology")
    price: float = Field(..., ge=0, example=45.0)
    normal_range: Optional[str] = Field(None, example="WBC: 4.5-11.0 x10^3/uL")

class LabTestResponse(BaseModel):
    id: str
    code: str
    name: str
    category: Optional[str] = None
    price: float
    normal_range: Optional[str] = None

    class Config:
        from_attributes = True

class LabOrderCreate(BaseModel):
    patient_id: str
    doctor_id: Optional[str] = None
    order_date: datetime = Field(default_factory=datetime.now)

class LabOrderResponse(BaseModel):
    id: str
    patient_id: str
    doctor_id: Optional[str] = None
    order_date: datetime
    status: LabOrderStatusEnum

    class Config:
        from_attributes = True

class LabSampleCreate(BaseModel):
    lab_order_id: str
    sample_type: str = Field(..., example="Venous Blood")
    collected_at: datetime = Field(default_factory=datetime.now)
    barcode: str = Field(..., example="SMP-8839201")

class LabSampleResponse(BaseModel):
    id: str
    lab_order_id: str
    sample_type: str
    collected_at: datetime
    barcode: str

    class Config:
        from_attributes = True

class LabResultCreate(BaseModel):
    lab_order_id: str
    lab_test_id: str
    result_value: str = Field(..., example="Hemoglobin: 14.2 g/dL (Normal)")
    remarks: Optional[str] = Field(None, example="All hematology markers within normal limits")
    verified_by: Optional[str] = Field(None, example="Dr. Lab Officer")

class LabResultResponse(BaseModel):
    id: str
    lab_order_id: str
    lab_test_id: str
    result_value: str
    remarks: Optional[str] = None
    verified_by: Optional[str] = None

    class Config:
        from_attributes = True

class MedicineCreate(BaseModel):
    code: str = Field(..., example="MED-PAR-500")
    name: str = Field(..., example="Paracetamol 500mg")
    generic_name: Optional[str] = Field(None, example="Acetaminophen")
    category: Optional[str] = Field(None, example="Analgesics")
    unit_price: float = Field(..., ge=0, example=0.50)

class MedicineResponse(BaseModel):
    id: str
    code: str
    name: str
    generic_name: Optional[str] = None
    category: Optional[str] = None
    unit_price: float

    class Config:
        from_attributes = True

class StockBatchCreate(BaseModel):
    medicine_id: str
    batch_number: str = Field(..., example="BATCH-2026-001")
    quantity: int = Field(..., ge=1, example=500)
    expiry_date: date = Field(..., example="2028-12-31")

class StockBatchResponse(BaseModel):
    id: str
    medicine_id: str
    batch_number: str
    quantity: int
    expiry_date: date

    class Config:
        from_attributes = True

class DispensingCreate(BaseModel):
    patient_id: str
    prescription_id: Optional[str] = None
    total_amount: float = Field(..., ge=0, example=25.50)

class DispensingResponse(BaseModel):
    id: str
    patient_id: str
    prescription_id: Optional[str] = None
    dispensed_date: datetime
    total_amount: float

    class Config:
        from_attributes = True

class InventoryItemCreate(BaseModel):
    item_name: str = Field(..., example="Surgical Gloves Size M")
    category: str = Field(..., example="Consumables")
    quantity_in_stock: int = Field(..., ge=0, example=1000)
    reorder_level: int = Field(100, ge=1, example=100)
    unit: str = Field(..., example="Pairs")

class InventoryItemResponse(BaseModel):
    id: str
    item_name: str
    category: str
    quantity_in_stock: int
    reorder_level: int
    unit: str

    class Config:
        from_attributes = True
