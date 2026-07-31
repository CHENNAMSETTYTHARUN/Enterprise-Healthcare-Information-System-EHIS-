from sqlalchemy import Column, String, DateTime, Date, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel

class AppointmentStatusEnum(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"

class Appointment(BaseModel):
    __tablename__ = "appointments"

    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(String(36), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    appointment_date = Column(DateTime, nullable=False, index=True)
    status = Column(Enum(AppointmentStatusEnum), default=AppointmentStatusEnum.SCHEDULED, nullable=False)
    reason = Column(Text, nullable=True)

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")

class OPDRecord(BaseModel):
    __tablename__ = "opd_records"

    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(String(36), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    visit_date = Column(DateTime, nullable=False)
    symptoms = Column(Text, nullable=False)
    diagnosis_notes = Column(Text, nullable=True)

    patient = relationship("Patient", back_populates="opd_records")
    doctor = relationship("Doctor", back_populates="opd_records")

class IPDRecord(BaseModel):
    __tablename__ = "ipd_records"

    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(String(36), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    bed_id = Column(String(36), ForeignKey("beds.id", ondelete="SET NULL"), nullable=True)
    admission_date = Column(DateTime, nullable=False)
    discharge_date = Column(DateTime, nullable=True)
    admission_reason = Column(Text, nullable=False)

    patient = relationship("Patient", back_populates="ipd_records")
    doctor = relationship("Doctor", back_populates="ipd_records")
    bed = relationship("Bed", back_populates="ipd_records")

class EMRRecord(BaseModel):
    __tablename__ = "emr_records"

    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(String(36), ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200), nullable=False)
    clinical_history = Column(Text, nullable=True)
    vitals = Column(Text, nullable=True)

    patient = relationship("Patient", back_populates="emr_records")

class Diagnosis(BaseModel):
    __tablename__ = "diagnoses"

    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    icd_code = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=False)
    diagnosed_date = Column(Date, nullable=False)

class TreatmentPlan(BaseModel):
    __tablename__ = "treatment_plans"

    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(String(36), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    objectives = Column(Text, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)

class Prescription(BaseModel):
    __tablename__ = "prescriptions"

    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(String(36), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    prescription_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)

    items = relationship("PrescriptionItem", back_populates="prescription", cascade="all, delete-orphan")

class PrescriptionItem(BaseModel):
    __tablename__ = "prescription_items"

    prescription_id = Column(String(36), ForeignKey("prescriptions.id", ondelete="CASCADE"), nullable=False)
    medicine_name = Column(String(150), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    duration = Column(String(50), nullable=False)

    prescription = relationship("Prescription", back_populates="items")

class ClinicalNote(BaseModel):
    __tablename__ = "clinical_notes"

    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(String(36), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    note_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)

class Surgery(BaseModel):
    __tablename__ = "surgeries"

    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    lead_surgeon_id = Column(String(36), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    surgery_name = Column(String(200), nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    operating_room = Column(String(50), nullable=True)
    status = Column(String(30), default="SCHEDULED")

class DischargeSummary(BaseModel):
    __tablename__ = "discharge_summaries"

    ipd_record_id = Column(String(36), ForeignKey("ipd_records.id", ondelete="CASCADE"), unique=True, nullable=False)
    summary = Column(Text, nullable=False)
    advice_on_discharge = Column(Text, nullable=True)
    follow_up_date = Column(Date, nullable=True)
