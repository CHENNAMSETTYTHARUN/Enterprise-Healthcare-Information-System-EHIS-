from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.repositories.clinical_repository import (
    appointment_repository, opd_repository, ipd_repository, emr_repository,
    diagnosis_repository, treatment_plan_repository, prescription_repository,
    clinical_note_repository, surgery_repository, discharge_summary_repository
)
from app.schemas.clinical import (
    AppointmentCreate, OPDCreate, IPDCreate, EMRCreate, DiagnosisCreate,
    TreatmentPlanCreate, PrescriptionCreate, ClinicalNoteCreate, SurgeryCreate, DischargeSummaryCreate
)
from app.models.clinical import (
    Appointment, OPDRecord, IPDRecord, EMRRecord, Diagnosis, TreatmentPlan,
    Prescription, PrescriptionItem, ClinicalNote, Surgery, DischargeSummary, AppointmentStatusEnum
)
from app.models.patient import BedStatusEnum
from app.repositories.patient_repository import bed_repository
from app.core.exceptions import NotFoundException

class ClinicalService:
    # Appointments
    def create_appointment(self, db: Session, appt_in: AppointmentCreate) -> Appointment:
        return appointment_repository.create(db, appt_in.model_dump())

    def get_appointments(self, db: Session, page: int, page_size: int, search: Optional[str]) -> Tuple[List[Appointment], int]:
        return appointment_repository.get_all(db, page=page, page_size=page_size, search=search, search_fields=["reason"])

    # OPD & IPD
    def create_opd_record(self, db: Session, opd_in: OPDCreate) -> OPDRecord:
        return opd_repository.create(db, opd_in.model_dump())

    def create_ipd_record(self, db: Session, ipd_in: IPDCreate) -> IPDRecord:
        if ipd_in.bed_id:
            bed = bed_repository.get_by_id(db, ipd_in.bed_id)
            if bed:
                bed_repository.update(db, bed, {"status": BedStatusEnum.OCCUPIED})
        return ipd_repository.create(db, ipd_in.model_dump())

    # EMR & Clinical Records
    def create_emr_record(self, db: Session, emr_in: EMRCreate) -> EMRRecord:
        return emr_repository.create(db, emr_in.model_dump())

    def create_diagnosis(self, db: Session, diag_in: DiagnosisCreate) -> Diagnosis:
        return diagnosis_repository.create(db, diag_in.model_dump())

    def create_treatment_plan(self, db: Session, tp_in: TreatmentPlanCreate) -> TreatmentPlan:
        return treatment_plan_repository.create(db, tp_in.model_dump())

    def create_prescription(self, db: Session, presc_in: PrescriptionCreate) -> Prescription:
        items_data = presc_in.items
        presc_dict = presc_in.model_dump(exclude={"items"})
        prescription = prescription_repository.create(db, presc_dict)

        for item in items_data:
            item_obj = PrescriptionItem(
                prescription_id=prescription.id,
                medicine_name=item.medicine_name,
                dosage=item.dosage,
                frequency=item.frequency,
                duration=item.duration
            )
            db.add(item_obj)
        db.commit()
        db.refresh(prescription)
        return prescription

    def create_clinical_note(self, db: Session, note_in: ClinicalNoteCreate) -> ClinicalNote:
        return clinical_note_repository.create(db, note_in.model_dump())

    def create_surgery(self, db: Session, surgery_in: SurgeryCreate) -> Surgery:
        return surgery_repository.create(db, surgery_in.model_dump())

    def create_discharge_summary(self, db: Session, ds_in: DischargeSummaryCreate) -> DischargeSummary:
        ds = discharge_summary_repository.create(db, ds_in.model_dump())
        ipd = ipd_repository.get_by_id(db, ds_in.ipd_record_id)
        if ipd and ipd.bed_id:
            bed = bed_repository.get_by_id(db, ipd.bed_id)
            if bed:
                bed_repository.update(db, bed, {"status": BedStatusEnum.AVAILABLE})
        return ds

clinical_service = ClinicalService()
