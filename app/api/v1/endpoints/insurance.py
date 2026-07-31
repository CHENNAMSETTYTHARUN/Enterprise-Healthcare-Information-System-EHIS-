from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.rbac import require_roles
from app.services.billing_service import billing_service
from app.repositories.billing_repository import insurance_claim_repository
from app.schemas.billing import ClaimCreate, ClaimResponse
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/insurance", tags=["Finance & Insurance"])

@router.post("/claims", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "ACCOUNTANT"]))])
def submit_insurance_claim(claim_in: ClaimCreate, db: Session = Depends(get_db)):
    """Submit insurance claim for invoice."""
    return billing_service.submit_claim(db, claim_in)

@router.get("/claims", response_model=PaginatedResponse[ClaimResponse])
def get_insurance_claims(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    items, total = insurance_claim_repository.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)

@router.put("/claims/{claim_id}/approve", response_model=ClaimResponse, dependencies=[Depends(require_roles(["SUPER_ADMIN", "ACCOUNTANT"]))])
def approve_claim(claim_id: str, approved_amount: float, db: Session = Depends(get_db)):
    """Approve insurance claim with approved reimbursement amount."""
    return billing_service.approve_claim(db, claim_id, approved_amount)
