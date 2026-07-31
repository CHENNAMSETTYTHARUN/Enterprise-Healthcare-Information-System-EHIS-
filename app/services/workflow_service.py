from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.clinical import Appointment, AppointmentStatusEnum
from app.models.billing import InsuranceClaim, ClaimStatusEnum

VALID_APPOINTMENT_TRANSITIONS = {
    AppointmentStatusEnum.SCHEDULED: [AppointmentStatusEnum.CONFIRMED, AppointmentStatusEnum.CANCELLED],
    AppointmentStatusEnum.CONFIRMED: [AppointmentStatusEnum.COMPLETED, AppointmentStatusEnum.CANCELLED, AppointmentStatusEnum.NO_SHOW],
    AppointmentStatusEnum.COMPLETED: [],
    AppointmentStatusEnum.CANCELLED: [],
    AppointmentStatusEnum.NO_SHOW: [AppointmentStatusEnum.SCHEDULED]
}

VALID_CLAIM_TRANSITIONS = {
    ClaimStatusEnum.SUBMITTED: [ClaimStatusEnum.UNDER_REVIEW],
    ClaimStatusEnum.UNDER_REVIEW: [ClaimStatusEnum.APPROVED, ClaimStatusEnum.REJECTED],
    ClaimStatusEnum.APPROVED: [],
    ClaimStatusEnum.REJECTED: [ClaimStatusEnum.SUBMITTED]
}

class WorkflowService:
    def transition_appointment(self, db: Session, appointment_id: str, new_status: str, user_id: str):
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

        try:
            new_status_enum = AppointmentStatusEnum(new_status)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {new_status}")

        allowed = VALID_APPOINTMENT_TRANSITIONS.get(appointment.status, [])
        if new_status_enum not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot transition from {appointment.status.value} to {new_status}. Allowed: {[s.value for s in allowed]}"
            )

        old_status = appointment.status.value
        appointment.status = new_status_enum
        db.commit()
        db.refresh(appointment)

        return {
            "appointment_id": appointment_id,
            "previous_status": old_status,
            "new_status": new_status_enum.value,
            "transitioned_at": datetime.now(timezone.utc).isoformat()
        }

    def transition_claim(self, db: Session, claim_id: str, new_status: str, remarks: str = None):
        claim = db.query(InsuranceClaim).filter(InsuranceClaim.id == claim_id).first()
        if not claim:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insurance claim not found")

        try:
            new_status_enum = ClaimStatusEnum(new_status)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {new_status}")

        allowed = VALID_CLAIM_TRANSITIONS.get(claim.status, [])
        if new_status_enum not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot transition from {claim.status.value} to {new_status}. Allowed: {[s.value for s in allowed]}"
            )

        old_status = claim.status.value
        claim.status = new_status_enum
        if remarks:
            claim.remarks = remarks
        if new_status_enum == ClaimStatusEnum.UNDER_REVIEW:
            claim.submitted_at = datetime.now(timezone.utc)
        elif new_status_enum in [ClaimStatusEnum.APPROVED, ClaimStatusEnum.REJECTED]:
            claim.reviewed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(claim)

        return {
            "claim_id": claim_id,
            "previous_status": old_status,
            "new_status": new_status_enum.value,
            "transitioned_at": datetime.now(timezone.utc).isoformat()
        }

workflow_service = WorkflowService()
