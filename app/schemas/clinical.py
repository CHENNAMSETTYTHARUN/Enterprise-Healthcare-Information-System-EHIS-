from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, Field
from app.models.clinical import AppointmentStatusEnum

class AppointmentCreate(BaseModel):
    patient_id: str
    doctor_id: str
    appointment_date: datetime = Field(..., example="2026-08-05T10:30:00")
    reason: Optional[str] = Field(None, example="Routine cardiology consultation")

class AppointmentResponse(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    appointment_date: datetime
    status: AppointmentStatusEnum
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class OPDCreate(BaseModel):
    patient_id: str
    doctor_id: str
    visit_date: datetime = Field(default_factory=datetime.now)
    symptoms: str = Field(..., example="Fever, cough for 3 days")
    diagnosis_notes: Optional[str] = Field(None, example="Mild upper respiratory infection")

class OPDResponse(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    visit_date: datetime
    symptoms: str
    diagnosis_notes: Optional[str] = None

    class Config:
        from_attributes = True

class IPDCreate(BaseModel):
    patient_id: str
    doctor_id: str
    bed_id: Optional[str] = None
    admission_date: datetime = Field(default_factory=datetime.now)
    admission_reason: str = Field(..., example="Severe pneumonia observation")

class IPDResponse(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    bed_id: Optional[str] = None
    admission_date: datetime
    discharge_date: Optional[datetime] = None
    admission_reason: str

    class Config:
        from_attributes = True

class EMRCreate(BaseModel):
    patient_id: str
    doctor_id: Optional[str] = None
    title: str = Field(..., example="Annual Health Assessment")
    clinical_history: Optional[str] = Field(None, example="Hypertension controlled with medication")
    vitals: Optional[str] = Field(None, example="BP: 120/80 mmHg, Pulse: 72 bpm, Temp: 98.6F")

class EMRResponse(BaseModel):
    id: str
    patient_id: str
    doctor_id: Optional[str] = None
    title: str
    clinical_history: Optional[str] = None
    vitals: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DiagnosisCreate(BaseModel):
    patient_id: str
    icd_code: str = Field(..., example="I10")
    description: str = Field(..., example="Essential (primary) hypertension")
    diagnosed_date: date = Field(..., example="2026-08-01")

class DiagnosisResponse(BaseModel):
    id: str
    patient_id: str
    icd_code: str
    description: str
    diagnosed_date: date

    class Config:
        from_attributes = True

class TreatmentPlanCreate(BaseModel):
    patient_id: str
    doctor_id: str
    title: str = Field(..., example="Cardiac Rehabilitation Plan")
    objectives: str = Field(..., example="Improve aerobic capacity, lower cholesterol")
    start_date: date = Field(..., example="2026-08-01")
    end_date: Optional[date] = None

class TreatmentPlanResponse(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    title: str
    objectives: str
    start_date: date
    end_date: Optional[date] = None

    class Config:
        from_attributes = True

class PrescriptionItemCreate(BaseModel):
    medicine_name: str = Field(..., example="Amoxicillin 500mg")
    dosage: str = Field(..., example="1 capsule")
    frequency: str = Field(..., example="Three times daily")
    duration: str = Field(..., example="7 days")

class PrescriptionCreate(BaseModel):
    patient_id: str
    doctor_id: str
    prescription_date: date = Field(default_factory=date.today)
    notes: Optional[str] = Field(None, example="Take after meals")
    items: List[PrescriptionItemCreate]

class PrescriptionItemResponse(BaseModel):
    id: str
    medicine_name: str
    dosage: str
    frequency: str
    duration: str

    class Config:
        from_attributes = True

class PrescriptionResponse(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    prescription_date: date
    notes: Optional[str] = None
    items: List[PrescriptionItemResponse] = []

    class Config:
        from_attributes = True

class ClinicalNoteCreate(BaseModel):
    patient_id: str
    doctor_id: str
    note_type: str = Field(..., example="SOAP")
    content: str = Field(..., example="Subjective: Patient reports feeling better. Objective: Clear lung sounds.")

class ClinicalNoteResponse(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    note_type: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class SurgeryCreate(BaseModel):
    patient_id: str
    lead_surgeon_id: str
    surgery_name: str = Field(..., example="Appendectomy")
    scheduled_date: datetime = Field(..., example="2026-08-10T08:00:00")
    operating_room: Optional[str] = Field(None, example="OR-2")

class SurgeryResponse(BaseModel):
    id: str
    patient_id: str
    lead_surgeon_id: str
    surgery_name: str
    scheduled_date: datetime
    operating_room: Optional[str] = None
    status: str

    class Config:
        from_attributes = True

class DischargeSummaryCreate(BaseModel):
    ipd_record_id: str
    summary: str = Field(..., example="Patient successfully treated for acute bronchitis. Condition stable upon discharge.")
    advice_on_discharge: Optional[str] = Field(None, example="Rest for 5 days, drink fluids.")
    follow_up_date: Optional[date] = Field(None, example="2026-08-20")

class DischargeSummaryResponse(BaseModel):
    id: str
    ipd_record_id: str
    summary: str
    advice_on_discharge: Optional[str] = None
    follow_up_date: Optional[date] = None

    class Config:
        from_attributes = True
