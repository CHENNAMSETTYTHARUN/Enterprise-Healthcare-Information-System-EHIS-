from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.workflow_service import workflow_service

router = APIRouter(prefix="/workflow", tags=["Workflow Engine"])

class AppointmentTransition(BaseModel):
    new_status: str

class ClaimTransition(BaseModel):
    new_status: str
    remarks: Optional[str] = None

@router.post("/appointments/{appointment_id}/transition")
def transition_appointment(
    appointment_id: str,
    body: AppointmentTransition,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return workflow_service.transition_appointment(db, appointment_id, body.new_status, current_user.id)

@router.post("/claims/{claim_id}/transition")
def transition_claim(
    claim_id: str,
    body: ClaimTransition,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return workflow_service.transition_claim(db, claim_id, body.new_status, body.remarks)

@router.get("/appointments/valid-transitions")
def get_appointment_transitions(current_user: User = Depends(get_current_user)):
    from app.services.workflow_service import VALID_APPOINTMENT_TRANSITIONS
    return {
        k.value: [v.value for v in values]
        for k, values in VALID_APPOINTMENT_TRANSITIONS.items()
    }

@router.get("/claims/valid-transitions")
def get_claim_transitions(current_user: User = Depends(get_current_user)):
    from app.services.workflow_service import VALID_CLAIM_TRANSITIONS
    return {
        k.value: [v.value for v in values]
        for k, values in VALID_CLAIM_TRANSITIONS.items()
    }
