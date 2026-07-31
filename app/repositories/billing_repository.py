from app.models.billing import Invoice, InvoiceItem, Payment, InsuranceClaim, Refund
from app.repositories.base import BaseRepository

class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self):
        super().__init__(Invoice)

class InvoiceItemRepository(BaseRepository[InvoiceItem]):
    def __init__(self):
        super().__init__(InvoiceItem)

class PaymentRepository(BaseRepository[Payment]):
    def __init__(self):
        super().__init__(Payment)

class InsuranceClaimRepository(BaseRepository[InsuranceClaim]):
    def __init__(self):
        super().__init__(InsuranceClaim)

class RefundRepository(BaseRepository[Refund]):
    def __init__(self):
        super().__init__(Refund)

invoice_repository = InvoiceRepository()
invoice_item_repository = InvoiceItemRepository()
payment_repository = PaymentRepository()
insurance_claim_repository = InsuranceClaimRepository()
refund_repository = RefundRepository()
