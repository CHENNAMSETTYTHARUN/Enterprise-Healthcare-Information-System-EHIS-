from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.patient import Patient, Bed, Emergency, BedStatusEnum
from app.models.hospital import Doctor, Department
from app.models.clinical import Appointment, OPDRecord, IPDRecord
from app.models.lab_pharmacy import LabOrder, Medicine, StockBatch
from app.models.billing import Invoice, InsuranceClaim, Refund, ClaimStatusEnum
from app.models.audit import AuditLog
from app.schemas.analytics import DashboardStatsResponse, RevenueAnalyticsResponse, DepartmentOccupancyResponse

class AnalyticsService:
    def get_dashboard_stats(self, db: Session) -> DashboardStatsResponse:
        total_patients = db.query(func.count(Patient.id)).filter(Patient.is_active == True).scalar() or 0
        total_doctors = db.query(func.count(Doctor.id)).filter(Doctor.is_active == True).scalar() or 0
        total_appointments_today = db.query(func.count(Appointment.id)).filter(Appointment.is_active == True).scalar() or 0
        active_emergencies = db.query(func.count(Emergency.id)).filter(Emergency.is_active == True).scalar() or 0

        occupied_beds = db.query(func.count(Bed.id)).filter(Bed.status == BedStatusEnum.OCCUPIED, Bed.is_active == True).scalar() or 0
        available_beds = db.query(func.count(Bed.id)).filter(Bed.status == BedStatusEnum.AVAILABLE, Bed.is_active == True).scalar() or 0

        total_revenue = db.query(func.sum(Invoice.paid_amount)).filter(Invoice.is_active == True).scalar() or 0.0

        total_lab_orders = db.query(func.count(LabOrder.id)).filter(LabOrder.is_active == True).scalar() or 0
        total_opd = db.query(func.count(OPDRecord.id)).filter(OPDRecord.is_active == True).scalar() or 0
        total_ipd = db.query(func.count(IPDRecord.id)).filter(IPDRecord.is_active == True).scalar() or 0

        from datetime import date
        today = date.today()
        threshold = today + timedelta(days=30)
        expiring_medicines = db.query(func.count(StockBatch.id)).filter(
            StockBatch.expiry_date <= threshold,
            StockBatch.quantity > 0,
            StockBatch.is_active == True
        ).scalar() or 0

        return DashboardStatsResponse(
            total_patients=total_patients,
            total_doctors=total_doctors,
            total_appointments_today=total_appointments_today,
            active_emergencies=active_emergencies,
            total_revenue_month=float(total_revenue),
            occupied_beds=occupied_beds,
            available_beds=available_beds,
            total_lab_orders=total_lab_orders,
            total_opd_visits=total_opd,
            total_ipd_admissions=total_ipd,
            medicines_expiring_soon=expiring_medicines
        )

    def get_revenue_analytics(self, db: Session) -> RevenueAnalyticsResponse:
        total_billed = db.query(func.sum(Invoice.total_amount)).filter(Invoice.is_active == True).scalar() or 0.0
        total_collected = db.query(func.sum(Invoice.paid_amount)).filter(Invoice.is_active == True).scalar() or 0.0
        total_tax = db.query(func.sum(Invoice.tax_amount)).filter(Invoice.is_active == True).scalar() or 0.0
        total_discount = db.query(func.sum(Invoice.discount_amount)).filter(Invoice.is_active == True).scalar() or 0.0
        outstanding = float(total_billed) - float(total_collected)

        pending_claims = db.query(func.count(InsuranceClaim.id)).filter(
            InsuranceClaim.status == ClaimStatusEnum.SUBMITTED,
            InsuranceClaim.is_active == True
        ).scalar() or 0

        approved_claims = db.query(func.sum(InsuranceClaim.approved_amount)).filter(
            InsuranceClaim.status == ClaimStatusEnum.APPROVED,
            InsuranceClaim.is_active == True
        ).scalar() or 0.0

        total_refunds = db.query(func.sum(Refund.amount)).filter(
            Refund.is_approved == True,
            Refund.is_active == True
        ).scalar() or 0.0

        return RevenueAnalyticsResponse(
            total_billed=float(total_billed),
            total_collected=float(total_collected),
            outstanding_balance=max(0.0, outstanding),
            claims_pending_approval=pending_claims,
            total_tax_collected=float(total_tax),
            total_discounts_given=float(total_discount),
            insurance_recovered=float(approved_claims),
            total_refunds=float(total_refunds),
            net_revenue=float(total_collected) - float(total_refunds)
        )

    def get_patient_trends(self, db: Session, days: int = 30):
        result = []
        today = datetime.now(timezone.utc).date()
        for i in range(days - 1, -1, -1):
            day = today - timedelta(days=i)
            day_start = datetime(day.year, day.month, day.day, 0, 0, 0)
            day_end = datetime(day.year, day.month, day.day, 23, 59, 59)
            count = db.query(func.count(Patient.id)).filter(
                Patient.created_at >= day_start,
                Patient.created_at <= day_end
            ).scalar() or 0
            result.append({"date": str(day), "new_patients": count})
        return {"days": days, "trend": result}

    def get_department_occupancy(self, db: Session):
        departments = db.query(Department).filter(Department.is_active == True).all()
        result = []
        for dept in departments:
            doctor_count = db.query(func.count(Doctor.id)).filter(Doctor.department_id == dept.id, Doctor.is_active == True).scalar() or 0
            appointment_count = db.query(func.count(Appointment.id)).join(Doctor, Appointment.doctor_id == Doctor.id).filter(Doctor.department_id == dept.id, Appointment.is_active == True).scalar() or 0
            result.append({
                "department_id": dept.id,
                "department_name": dept.name,
                "doctor_count": doctor_count,
                "total_appointments": appointment_count
            })
        return {"departments": result}

analytics_service = AnalyticsService()
