import logging
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.audit import AuditLog, Notification

logger = logging.getLogger("ehis.background")

def send_email_notification(recipient_email: str, subject: str, body: str) -> None:
    logger.info(f"[EMAIL] To: {recipient_email} | Subject: {subject}")

def send_sms_notification(phone_number: str, message: str) -> None:
    logger.info(f"[SMS] To: {phone_number} | Message: {message}")

def log_audit_event(user_id: str, action: str, details: Dict[str, Any]) -> None:
    logger.info(f"[AUDIT] User: {user_id} | Action: {action} | Details: {details}")
    db: Session = SessionLocal()
    try:
        audit_log = AuditLog(
            user_id=user_id if user_id else None,
            action=action,
            endpoint=details.get("endpoint"),
            ip_address=details.get("ip"),
            details=details
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        logger.error(f"[AUDIT] Failed to save audit log: {e}")
        db.rollback()
    finally:
        db.close()

def create_notification(user_id: str, title: str, message: str) -> None:
    db: Session = SessionLocal()
    try:
        notification = Notification(
            recipient_user_id=user_id,
            title=title,
            message=message,
            is_read="FALSE"
        )
        db.add(notification)
        db.commit()
    except Exception as e:
        logger.error(f"[NOTIFICATION] Failed to create notification: {e}")
        db.rollback()
    finally:
        db.close()

def process_lab_result_notification(patient_id: str, test_name: str, result_summary: str) -> None:
    logger.info(f"[LAB] Patient: {patient_id} | Test: {test_name} | Result: {result_summary}")

def process_invoice_notification(patient_id: str, invoice_number: str, amount: float) -> None:
    logger.info(f"[BILLING] Patient: {patient_id} | Invoice: {invoice_number} | Amount: {amount}")

def check_medicine_expiry() -> None:
    from datetime import date, timedelta
    from app.models.lab_pharmacy import StockBatch

    db: Session = SessionLocal()
    try:
        today = date.today()
        threshold = today + timedelta(days=30)
        expiring = db.query(StockBatch).filter(
            StockBatch.expiry_date <= threshold,
            StockBatch.quantity > 0
        ).all()
        if expiring:
            logger.warning(f"[EXPIRY CHECK] {len(expiring)} medicine batches expiring within 30 days")
            for batch in expiring:
                logger.warning(f"  Batch: {batch.batch_number} | Expiry: {batch.expiry_date} | Qty: {batch.quantity}")
    except Exception as e:
        logger.error(f"[EXPIRY CHECK] Error: {e}")
    finally:
        db.close()

def cleanup_inactive_sessions() -> None:
    from datetime import timedelta
    from app.models.user import UserSession

    db: Session = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        old_sessions = db.query(UserSession).filter(
            UserSession.last_active < cutoff
        ).all()
        for s in old_sessions:
            s.is_active = False
        db.commit()
        logger.info(f"[SESSION CLEANUP] Deactivated {len(old_sessions)} old sessions")
    except Exception as e:
        logger.error(f"[SESSION CLEANUP] Error: {e}")
        db.rollback()
    finally:
        db.close()
