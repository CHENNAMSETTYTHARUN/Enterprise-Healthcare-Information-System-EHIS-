from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.billing_service import billing_service
from app.repositories.billing_repository import invoice_repository, payment_repository, refund_repository
from app.schemas.billing import (
    InvoiceCreate, InvoiceResponse, PaymentCreate, PaymentResponse,
    RefundCreate, RefundResponse, ClaimApproveRequest, ClaimRejectRequest
)
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/billing", tags=["Finance & Billing"])

@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    inv_in: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return billing_service.create_invoice(db, inv_in)

@router.get("/invoices", response_model=PaginatedResponse[InvoiceResponse])
def get_invoices(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items, total = invoice_repository.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)

@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    invoice = invoice_repository.get_by_id(db, invoice_id)
    if not invoice:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def process_payment(
    pay_in: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return billing_service.record_payment(db, pay_in)

@router.get("/payments", response_model=PaginatedResponse[PaymentResponse])
def get_payments(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items, total = payment_repository.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)

@router.post("/refunds", response_model=RefundResponse, status_code=status.HTTP_201_CREATED)
def process_refund(
    ref_in: RefundCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return billing_service.process_refund(db, ref_in)

@router.get("/refunds", response_model=PaginatedResponse[RefundResponse])
def get_refunds(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items, total = refund_repository.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)

@router.post("/claims/{claim_id}/approve")
def approve_claim(
    claim_id: str,
    body: ClaimApproveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return billing_service.approve_claim(db, claim_id, body.approved_amount, body.remarks)

@router.post("/claims/{claim_id}/reject")
def reject_claim(
    claim_id: str,
    body: ClaimRejectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return billing_service.reject_claim(db, claim_id, body.remarks)
