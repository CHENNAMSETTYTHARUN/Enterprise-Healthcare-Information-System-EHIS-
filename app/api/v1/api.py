from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, hospital, branch, department, doctor, staff,
    patient, room_bed, emergency, appointment, opd_ipd, emr,
    surgery, lab, pharmacy, billing, insurance, notifications,
    analytics, audit, mfa, documents, search, reports, workflow
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(mfa.router)
api_router.include_router(users.router)
api_router.include_router(hospital.router)
api_router.include_router(branch.router)
api_router.include_router(department.router)
api_router.include_router(doctor.router)
api_router.include_router(staff.router)
api_router.include_router(patient.router)
api_router.include_router(room_bed.router)
api_router.include_router(emergency.router)
api_router.include_router(appointment.router)
api_router.include_router(opd_ipd.router)
api_router.include_router(emr.router)
api_router.include_router(surgery.router)
api_router.include_router(lab.router)
api_router.include_router(pharmacy.router)
api_router.include_router(billing.router)
api_router.include_router(insurance.router)
api_router.include_router(notifications.router)
api_router.include_router(analytics.router)
api_router.include_router(audit.router)
api_router.include_router(documents.router)
api_router.include_router(search.router)
api_router.include_router(reports.router)
api_router.include_router(workflow.router)
