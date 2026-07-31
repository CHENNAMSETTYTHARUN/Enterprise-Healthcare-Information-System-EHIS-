from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.patient import Patient
from app.models.clinical import Appointment, OPDRecord, IPDRecord
from app.models.lab_pharmacy import LabOrder, Medicine, StockBatch
from app.models.billing import Invoice, Payment, Refund, InsuranceClaim, InvoiceStatusEnum, ClaimStatusEnum
from app.models.hospital import Doctor, Department
from app.models.audit import AuditLog

class ReportService:
    def get_patient_report(self, db: Session, patient_id: str):
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            return None

        appointments = db.query(Appointment).filter(Appointment.patient_id == patient_id).count()
        opd_visits = db.query(OPDRecord).filter(OPDRecord.patient_id == patient_id).count()
        ipd_admissions = db.query(IPDRecord).filter(IPDRecord.patient_id == patient_id).count()
        lab_orders = db.query(LabOrder).filter(LabOrder.patient_id == patient_id).count()

        invoices = db.query(Invoice).filter(Invoice.patient_id == patient_id).all()
        total_billed = sum(float(inv.total_amount) for inv in invoices)
        total_paid = sum(float(inv.paid_amount) for inv in invoices)

        return {
            "report_type": "Patient Summary",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "patient": {
                "id": patient.id,
                "name": f"{patient.first_name} {patient.last_name}",
                "mrn": patient.mrn,
                "gender": patient.gender,
                "date_of_birth": str(patient.date_of_birth),
                "blood_group": patient.blood_group
            },
            "clinical_summary": {
                "total_appointments": appointments,
                "total_opd_visits": opd_visits,
                "total_ipd_admissions": ipd_admissions,
                "total_lab_orders": lab_orders
            },
            "billing_summary": {
                "total_invoices": len(invoices),
                "total_billed": total_billed,
                "total_paid": total_paid,
                "outstanding": total_billed - total_paid
            }
        }

    def get_financial_report(self, db: Session, start_date: datetime = None, end_date: datetime = None):
        if not start_date:
            start_date = datetime.now(timezone.utc) - timedelta(days=30)
        if not end_date:
            end_date = datetime.now(timezone.utc)

        invoices = db.query(Invoice).filter(
            Invoice.created_at >= start_date,
            Invoice.created_at <= end_date
        ).all()

        total_revenue = sum(float(inv.paid_amount) for inv in invoices)
        total_billed = sum(float(inv.total_amount) for inv in invoices)
        total_outstanding = total_billed - total_revenue
        total_tax = sum(float(inv.tax_amount) for inv in invoices)

        paid_count = sum(1 for inv in invoices if inv.status == InvoiceStatusEnum.PAID)
        unpaid_count = sum(1 for inv in invoices if inv.status == InvoiceStatusEnum.UNPAID)

        claims = db.query(InsuranceClaim).filter(
            InsuranceClaim.created_at >= start_date,
            InsuranceClaim.created_at <= end_date
        ).all()
        approved_claims = sum(float(c.approved_amount) for c in claims if c.status == ClaimStatusEnum.APPROVED)

        refunds = db.query(Refund).filter(
            Refund.created_at >= start_date,
            Refund.created_at <= end_date,
            Refund.is_approved == True
        ).all()
        total_refunds = sum(float(r.amount) for r in refunds)

        return {
            "report_type": "Financial Report",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period": {"from": start_date.isoformat(), "to": end_date.isoformat()},
            "revenue": {
                "total_billed": total_billed,
                "total_collected": total_revenue,
                "total_outstanding": total_outstanding,
                "total_tax_collected": total_tax,
                "insurance_recovered": approved_claims,
                "total_refunds": total_refunds,
                "net_revenue": total_revenue - total_refunds
            },
            "invoice_breakdown": {
                "total_invoices": len(invoices),
                "paid": paid_count,
                "unpaid": unpaid_count,
                "partially_paid": len(invoices) - paid_count - unpaid_count
            },
            "insurance": {
                "total_claims": len(claims),
                "approved_amount": approved_claims
            }
        }

    def get_department_report(self, db: Session, department_id: str = None):
        query = db.query(Department)
        if department_id:
            query = query.filter(Department.id == department_id)
        departments = query.all()

        result = []
        for dept in departments:
            doctor_count = db.query(Doctor).filter(Doctor.department_id == dept.id).count()
            appointment_count = db.query(Appointment).join(Doctor, Appointment.doctor_id == Doctor.id).filter(Doctor.department_id == dept.id).count()

            result.append({
                "department": {"id": dept.id, "name": dept.name},
                "doctor_count": doctor_count,
                "total_appointments": appointment_count
            })

        return {
            "report_type": "Department Report",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "departments": result
        }

    def get_pharmacy_report(self, db: Session):
        from datetime import date
        today = date.today()

        medicines = db.query(Medicine).all()
        expiring_soon = db.query(StockBatch).filter(
            StockBatch.expiry_date <= (today + timedelta(days=30))
        ).all()
        expired = db.query(StockBatch).filter(
            StockBatch.expiry_date < today
        ).all()
        low_stock = db.query(StockBatch).filter(StockBatch.quantity <= 10).all()

        return {
            "report_type": "Pharmacy Inventory Report",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_medicines": len(medicines),
                "expiring_in_30_days": len(expiring_soon),
                "expired_batches": len(expired),
                "low_stock_batches": len(low_stock)
            },
            "expiring_soon": [
                {"medicine_id": b.medicine_id, "batch_number": b.batch_number, "quantity": b.quantity, "expiry_date": str(b.expiry_date)}
                for b in expiring_soon
            ],
            "expired": [
                {"medicine_id": b.medicine_id, "batch_number": b.batch_number, "quantity": b.quantity, "expiry_date": str(b.expiry_date)}
                for b in expired
            ],
            "low_stock": [
                {"medicine_id": b.medicine_id, "batch_number": b.batch_number, "quantity": b.quantity}
                for b in low_stock
            ]
        }

    def get_audit_report(self, db: Session, start_date: datetime = None, end_date: datetime = None, action: str = None):
        if not start_date:
            start_date = datetime.now(timezone.utc) - timedelta(days=7)
        if not end_date:
            end_date = datetime.now(timezone.utc)

        query = db.query(AuditLog).filter(
            AuditLog.created_at >= start_date,
            AuditLog.created_at <= end_date
        )
        if action:
            query = query.filter(AuditLog.action == action)

        logs = query.order_by(AuditLog.created_at.desc()).limit(500).all()

        return {
            "report_type": "Audit Report",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period": {"from": start_date.isoformat(), "to": end_date.isoformat()},
            "total_events": len(logs),
            "events": [
                {"id": l.id, "user_id": l.user_id, "action": l.action, "endpoint": l.endpoint, "ip_address": l.ip_address, "created_at": l.created_at.isoformat() if l.created_at else None}
                for l in logs
            ]
        }

report_service = ReportService()
