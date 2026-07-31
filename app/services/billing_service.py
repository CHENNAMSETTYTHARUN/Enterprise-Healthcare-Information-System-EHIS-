from typing import List, Tuple, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.billing_repository import (
    invoice_repository, invoice_item_repository, payment_repository,
    insurance_claim_repository, refund_repository
)
from app.schemas.billing import (
    InvoiceCreate, PaymentCreate, ClaimCreate, RefundCreate
)
from app.models.billing import (
    Invoice, InvoiceItem, Payment, InsuranceClaim, Refund, InvoiceStatusEnum, ClaimStatusEnum
)
from app.core.exceptions import NotFoundException, BadRequestException

class BillingService:
    def create_invoice(self, db: Session, inv_in: InvoiceCreate) -> Invoice:
        items_data = inv_in.items
        subtotal = sum(item.unit_price * item.quantity for item in items_data)

        tax_rate = float(getattr(inv_in, 'tax_rate', 0.0) or 0.0)
        discount_amount = float(getattr(inv_in, 'discount_amount', 0.0) or 0.0)
        tax_amount = round(subtotal * (tax_rate / 100), 2)
        total_amount = subtotal + tax_amount - discount_amount

        invoice = Invoice(
            invoice_number=inv_in.invoice_number,
            patient_id=inv_in.patient_id,
            issue_date=inv_in.issue_date or datetime.now(timezone.utc),
            subtotal=subtotal,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            total_amount=total_amount,
            paid_amount=0.0,
            status=InvoiceStatusEnum.UNPAID
        )
        db.add(invoice)
        db.flush()

        for item in items_data:
            item_obj = InvoiceItem(
                invoice_id=invoice.id,
                description=item.description,
                unit_price=item.unit_price,
                quantity=item.quantity,
                total_price=item.unit_price * item.quantity
            )
            db.add(item_obj)

        db.commit()
        db.refresh(invoice)
        return invoice

    def record_payment(self, db: Session, pay_in: PaymentCreate) -> Payment:
        invoice = invoice_repository.get_by_id(db, pay_in.invoice_id)
        if not invoice:
            raise NotFoundException(f"Invoice with ID '{pay_in.invoice_id}' not found")

        if invoice.status == InvoiceStatusEnum.PAID:
            raise BadRequestException("Invoice is already fully paid")

        if invoice.status == InvoiceStatusEnum.CANCELLED:
            raise BadRequestException("Cannot pay a cancelled invoice")

        payment = payment_repository.create(db, pay_in.model_dump())

        new_paid_amount = float(invoice.paid_amount) + pay_in.amount
        new_status = InvoiceStatusEnum.PAID if new_paid_amount >= float(invoice.total_amount) else InvoiceStatusEnum.PARTIALLY_PAID

        invoice_repository.update(db, invoice, {
            "paid_amount": new_paid_amount,
            "status": new_status
        })

        return payment

    def submit_claim(self, db: Session, claim_in: ClaimCreate) -> InsuranceClaim:
        return insurance_claim_repository.create(db, claim_in.model_dump())

    def approve_claim(self, db: Session, claim_id: str, approved_amount: float, remarks: str = None) -> InsuranceClaim:
        claim = insurance_claim_repository.get_by_id(db, claim_id)
        if not claim:
            raise NotFoundException(f"Claim '{claim_id}' not found")

        if claim.status not in [ClaimStatusEnum.SUBMITTED, ClaimStatusEnum.UNDER_REVIEW]:
            raise BadRequestException(f"Claim with status '{claim.status.value}' cannot be approved")

        return insurance_claim_repository.update(db, claim, {
            "approved_amount": approved_amount,
            "status": ClaimStatusEnum.APPROVED,
            "reviewed_at": datetime.now(timezone.utc),
            "remarks": remarks or claim.remarks
        })

    def reject_claim(self, db: Session, claim_id: str, remarks: str) -> InsuranceClaim:
        claim = insurance_claim_repository.get_by_id(db, claim_id)
        if not claim:
            raise NotFoundException(f"Claim '{claim_id}' not found")

        if claim.status not in [ClaimStatusEnum.SUBMITTED, ClaimStatusEnum.UNDER_REVIEW]:
            raise BadRequestException(f"Claim with status '{claim.status.value}' cannot be rejected")

        return insurance_claim_repository.update(db, claim, {
            "status": ClaimStatusEnum.REJECTED,
            "reviewed_at": datetime.now(timezone.utc),
            "remarks": remarks
        })

    def process_refund(self, db: Session, ref_in: RefundCreate) -> Refund:
        invoice = invoice_repository.get_by_id(db, ref_in.invoice_id)
        if not invoice:
            raise NotFoundException(f"Invoice '{ref_in.invoice_id}' not found")

        if float(invoice.paid_amount) < ref_in.amount:
            raise BadRequestException(f"Refund amount ({ref_in.amount}) exceeds paid amount ({invoice.paid_amount})")

        return refund_repository.create(db, ref_in.model_dump())

billing_service = BillingService()
