from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.mfa_service import mfa_service

router = APIRouter(prefix="/auth/mfa", tags=["MFA"])

class MFACode(BaseModel):
    code: str

@router.post("/setup")
def setup_mfa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return mfa_service.setup_mfa(db, current_user.id)

@router.post("/enable")
def enable_mfa(
    body: MFACode,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return mfa_service.enable_mfa(db, current_user.id, body.code)

@router.post("/disable")
def disable_mfa(
    body: MFACode,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return mfa_service.disable_mfa(db, current_user.id, body.code)

@router.get("/status")
def mfa_status(current_user: User = Depends(get_current_user)):
    return {
        "mfa_enabled": current_user.mfa_enabled,
        "email": current_user.email
    }
