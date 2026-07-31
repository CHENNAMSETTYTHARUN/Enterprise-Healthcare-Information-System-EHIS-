from fastapi import APIRouter, Depends, Query
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.report_service import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/patient/{patient_id}")
def patient_report(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report = report_service.get_patient_report(db, patient_id)
    if not report:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Patient not found")
    return report

@router.get("/financial")
def financial_report(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return report_service.get_financial_report(db, start_date, end_date)

@router.get("/departments")
def department_report(
    department_id: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return report_service.get_department_report(db, department_id)

@router.get("/pharmacy")
def pharmacy_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return report_service.get_pharmacy_report(db)

@router.get("/audit")
def audit_report(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    action: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return report_service.get_audit_report(db, start_date, end_date, action)
