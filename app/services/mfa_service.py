from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.core.security import generate_totp_secret, get_totp_provisioning_uri, verify_totp_code

class MFAService:
    def setup_mfa(self, db: Session, user_id: str):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if user.mfa_enabled:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is already enabled")

        secret = generate_totp_secret()
        user.mfa_secret = secret
        db.commit()

        provisioning_uri = get_totp_provisioning_uri(secret, user.email)

        return {
            "secret": secret,
            "provisioning_uri": provisioning_uri,
            "message": "Scan this QR code or enter the secret in your authenticator app, then call /auth/mfa/enable to activate"
        }

    def enable_mfa(self, db: Session, user_id: str, code: str):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not user.mfa_secret:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA setup not initiated. Call /auth/mfa/setup first")

        if not verify_totp_code(user.mfa_secret, code):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid TOTP code")

        user.mfa_enabled = True
        db.commit()

        return {"message": "MFA enabled successfully"}

    def disable_mfa(self, db: Session, user_id: str, code: str):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not user.mfa_enabled:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is not enabled")

        if not verify_totp_code(user.mfa_secret, code):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid TOTP code")

        user.mfa_enabled = False
        user.mfa_secret = None
        db.commit()

        return {"message": "MFA disabled successfully"}

    def verify_mfa(self, db: Session, user_id: str, code: str) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.mfa_enabled or not user.mfa_secret:
            return False
        return verify_totp_code(user.mfa_secret, code)

mfa_service = MFAService()
