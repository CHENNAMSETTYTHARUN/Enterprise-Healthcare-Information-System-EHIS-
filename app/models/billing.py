from sqlalchemy import Column, String, DateTime, Date, Text, Enum, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel

class InvoiceStatusEnum(str, enum.Enum):
    UNPAID = "UNPAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

class ClaimStatusEnum(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class Invoice(BaseModel):
    __tablename__ = "invoices"

    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    issue_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=True)
    subtotal = Column(Numeric(10, 2), nullable=False, default=0.0)
    tax_rate = Column(Numeric(5, 2), nullable=False, default=0.0)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0.0)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0.0)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0.0)
    paid_amount = Column(Numeric(10, 2), nullable=False, default=0.0)
    notes = Column(Text, nullable=True)
    status = Column(Enum(InvoiceStatusEnum), default=InvoiceStatusEnum.UNPAID, nullable=False)

    patient = relationship("Patient", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")
    claims = relationship("InsuranceClaim", back_populates="invoice", cascade="all, delete-orphan")
    refunds = relationship("Refund", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(BaseModel):
    __tablename__ = "invoice_items"

    invoice_id = Column(String(36), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(String(200), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False, default=1.0)
    total_price = Column(Numeric(10, 2), nullable=False)

    invoice = relationship("Invoice", back_populates="items")

class Payment(BaseModel):
    __tablename__ = "payments"

    invoice_id = Column(String(36), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_method = Column(String(50), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    transaction_reference = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    invoice = relationship("Invoice", back_populates="payments")

class InsuranceClaim(BaseModel):
    __tablename__ = "insurance_claims"

    claim_number = Column(String(50), unique=True, nullable=False, index=True)
    invoice_id = Column(String(36), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    insurance_provider = Column(String(150), nullable=False)
    policy_number = Column(String(100), nullable=False)
    claimed_amount = Column(Numeric(10, 2), nullable=False)
    approved_amount = Column(Numeric(10, 2), default=0.0)
    status = Column(Enum(ClaimStatusEnum), default=ClaimStatusEnum.SUBMITTED, nullable=False)
    submitted_at = Column(DateTime, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    remarks = Column(Text, nullable=True)

    invoice = relationship("Invoice", back_populates="claims")

class Refund(BaseModel):
    __tablename__ = "refunds"

    invoice_id = Column(String(36), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_id = Column(String(36), ForeignKey("payments.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    reason = Column(Text, nullable=False)
    processed_by = Column(String(100), nullable=True)
    processed_date = Column(DateTime, nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False)

    invoice = relationship("Invoice", back_populates="refunds")
