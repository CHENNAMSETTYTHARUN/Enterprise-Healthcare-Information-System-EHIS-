from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.billing import InvoiceStatusEnum, ClaimStatusEnum

class InvoiceItemCreate(BaseModel):
    description: str = Field(..., example="Consultation Fee")
    unit_price: float = Field(..., ge=0, example=150.0)
    quantity: float = Field(1.0, ge=0.1, example=1.0)

class InvoiceCreate(BaseModel):
    invoice_number: str = Field(..., example="INV-2026-0001")
    patient_id: str
    issue_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    tax_rate: float = Field(0.0, ge=0, le=100, example=5.0)
    discount_amount: float = Field(0.0, ge=0, example=0.0)
    notes: Optional[str] = None
    items: List[InvoiceItemCreate]

class InvoiceItemResponse(BaseModel):
    id: str
    description: str
    unit_price: float
    quantity: float
    total_price: float

    class Config:
        from_attributes = True

class InvoiceResponse(BaseModel):
    id: str
    invoice_number: str
    patient_id: str
    issue_date: datetime
    subtotal: Optional[float] = 0.0
    tax_rate: Optional[float] = 0.0
    tax_amount: Optional[float] = 0.0
    discount_amount: Optional[float] = 0.0
    total_amount: float
    paid_amount: float
    status: InvoiceStatusEnum
    items: List[InvoiceItemResponse] = []

    class Config:
        from_attributes = True

class PaymentCreate(BaseModel):
    invoice_id: str
    payment_method: str = Field(..., example="Credit Card")
    amount: float = Field(..., ge=0.01, example=150.0)
    payment_date: Optional[datetime] = None
    transaction_reference: Optional[str] = Field(None, example="TXN-998822")
    notes: Optional[str] = None

class PaymentResponse(BaseModel):
    id: str
    invoice_id: str
    payment_method: str
    amount: float
    payment_date: datetime
    transaction_reference: Optional[str] = None

    class Config:
        from_attributes = True

class ClaimCreate(BaseModel):
    claim_number: str = Field(..., example="CLM-778811")
    invoice_id: str
    insurance_provider: str = Field(..., example="Blue Cross Health")
    policy_number: str = Field(..., example="POL-992211")
    claimed_amount: float = Field(..., ge=0.01, example=500.0)
    remarks: Optional[str] = None

class ClaimApproveRequest(BaseModel):
    approved_amount: float = Field(..., ge=0, example=450.0)
    remarks: Optional[str] = None

class ClaimRejectRequest(BaseModel):
    remarks: str = Field(..., example="Claim outside coverage period")

class ClaimResponse(BaseModel):
    id: str
    claim_number: str
    invoice_id: str
    insurance_provider: str
    policy_number: str
    claimed_amount: float
    approved_amount: float
    status: ClaimStatusEnum
    remarks: Optional[str] = None

    class Config:
        from_attributes = True

class RefundCreate(BaseModel):
    invoice_id: str
    payment_id: Optional[str] = None
    amount: float = Field(..., ge=0.01, example=50.0)
    reason: str = Field(..., example="Overpayment adjustment")
    processed_by: Optional[str] = None

class RefundResponse(BaseModel):
    id: str
    invoice_id: str
    amount: float
    reason: str
    processed_date: datetime
    is_approved: bool

    class Config:
        from_attributes = True
