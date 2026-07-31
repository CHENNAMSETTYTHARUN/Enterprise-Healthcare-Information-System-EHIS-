from app.models.clinical import (
    Appointment, OPDRecord, IPDRecord, EMRRecord, Diagnosis, TreatmentPlan,
    Prescription, PrescriptionItem, ClinicalNote, Surgery, DischargeSummary
)
from app.repositories.base import BaseRepository

class AppointmentRepository(BaseRepository[Appointment]):
    def __init__(self):
        super().__init__(Appointment)

class OPDRepository(BaseRepository[OPDRecord]):
    def __init__(self):
        super().__init__(OPDRecord)

class IPDRepository(BaseRepository[IPDRecord]):
    def __init__(self):
        super().__init__(IPDRecord)

class EMRRepository(BaseRepository[EMRRecord]):
    def __init__(self):
        super().__init__(EMRRecord)

class DiagnosisRepository(BaseRepository[Diagnosis]):
    def __init__(self):
        super().__init__(Diagnosis)

class TreatmentPlanRepository(BaseRepository[TreatmentPlan]):
    def __init__(self):
        super().__init__(TreatmentPlan)

class PrescriptionRepository(BaseRepository[Prescription]):
    def __init__(self):
        super().__init__(Prescription)

class ClinicalNoteRepository(BaseRepository[ClinicalNote]):
    def __init__(self):
        super().__init__(ClinicalNote)

class SurgeryRepository(BaseRepository[Surgery]):
    def __init__(self):
        super().__init__(Surgery)

class DischargeSummaryRepository(BaseRepository[DischargeSummary]):
    def __init__(self):
        super().__init__(DischargeSummary)

appointment_repository = AppointmentRepository()
opd_repository = OPDRepository()
ipd_repository = IPDRepository()
emr_repository = EMRRepository()
diagnosis_repository = DiagnosisRepository()
treatment_plan_repository = TreatmentPlanRepository()
prescription_repository = PrescriptionRepository()
clinical_note_repository = ClinicalNoteRepository()
surgery_repository = SurgeryRepository()
discharge_summary_repository = DischargeSummaryRepository()
