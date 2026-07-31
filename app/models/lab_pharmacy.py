from sqlalchemy import Column, String, DateTime, Date, Text, Enum, ForeignKey, Numeric, Integer
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel

class LabOrderStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    SAMPLE_COLLECTED = "SAMPLE_COLLECTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class LabTest(BaseModel):
    __tablename__ = "lab_tests"

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=True)
    price = Column(Numeric(10, 2), nullable=False, default=0.0)
    normal_range = Column(String(200), nullable=True)

class LabOrder(BaseModel):
    __tablename__ = "lab_orders"

    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(String(36), ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True)
    order_date = Column(DateTime, nullable=False)
    status = Column(Enum(LabOrderStatusEnum), default=LabOrderStatusEnum.PENDING, nullable=False)

    patient = relationship("Patient", back_populates="lab_orders")
    samples = relationship("LabSample", back_populates="lab_order", cascade="all, delete-orphan")
    results = relationship("LabResult", back_populates="lab_order", cascade="all, delete-orphan")

class LabSample(BaseModel):
    __tablename__ = "lab_samples"

    lab_order_id = Column(String(36), ForeignKey("lab_orders.id", ondelete="CASCADE"), nullable=False)
    sample_type = Column(String(50), nullable=False)
    collected_at = Column(DateTime, nullable=False)
    barcode = Column(String(100), unique=True, nullable=False)

    lab_order = relationship("LabOrder", back_populates="samples")

class LabResult(BaseModel):
    __tablename__ = "lab_results"

    lab_order_id = Column(String(36), ForeignKey("lab_orders.id", ondelete="CASCADE"), nullable=False)
    lab_test_id = Column(String(36), ForeignKey("lab_tests.id", ondelete="CASCADE"), nullable=False)
    result_value = Column(String(255), nullable=False)
    remarks = Column(Text, nullable=True)
    verified_by = Column(String(100), nullable=True)

    lab_order = relationship("LabOrder", back_populates="results")
    lab_test = relationship("LabTest")

class Medicine(BaseModel):
    __tablename__ = "medicines"

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False, index=True)
    generic_name = Column(String(150), nullable=True)
    category = Column(String(100), nullable=True)
    unit_price = Column(Numeric(10, 2), nullable=False, default=0.0)

    stock_batches = relationship("StockBatch", back_populates="medicine", cascade="all, delete-orphan")

class StockBatch(BaseModel):
    __tablename__ = "stock_batches"

    medicine_id = Column(String(36), ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False)
    batch_number = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    expiry_date = Column(Date, nullable=False)

    medicine = relationship("Medicine", back_populates="stock_batches")

class MedicineDispensing(BaseModel):
    __tablename__ = "medicine_dispensings"

    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    prescription_id = Column(String(36), ForeignKey("prescriptions.id", ondelete="SET NULL"), nullable=True)
    dispensed_date = Column(DateTime, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0.0)

class InventoryItem(BaseModel):
    __tablename__ = "inventory_items"

    item_name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False)
    quantity_in_stock = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, nullable=False, default=10)
    unit = Column(String(30), nullable=False)
