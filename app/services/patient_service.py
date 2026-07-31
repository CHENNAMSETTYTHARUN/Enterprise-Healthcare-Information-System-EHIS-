import random
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.repositories.patient_repository import (
    patient_repository, ward_repository, room_repository, bed_repository,
    emergency_repository, ambulance_repository
)
from app.schemas.patient import (
    PatientCreate, PatientUpdate, WardCreate, RoomCreate, BedCreate,
    EmergencyCreate, AmbulanceCreate
)
from app.models.patient import Patient, Ward, Room, Bed, Emergency, Ambulance, BedStatusEnum
from app.core.exceptions import NotFoundException, ConflictException

class PatientService:
    def generate_mrn(self) -> str:
        num = random.randint(100000, 999999)
        return f"MRN-{num}"

    def create_patient(self, db: Session, patient_in: PatientCreate) -> Patient:
        mrn = self.generate_mrn()
        while patient_repository.get_by_mrn(db, mrn):
            mrn = self.generate_mrn()

        data = patient_in.model_dump()
        data["mrn"] = mrn
        return patient_repository.create(db, data)

    def get_patient(self, db: Session, patient_id: str) -> Patient:
        patient = patient_repository.get_by_id(db, patient_id)
        if not patient:
            raise NotFoundException(f"Patient with ID '{patient_id}' not found")
        return patient

    def get_all_patients(
        self, db: Session, page: int, page_size: int, search: Optional[str], sort_by: Optional[str], sort_order: str
    ) -> Tuple[List[Patient], int]:
        return patient_repository.get_all(
            db, page=page, page_size=page_size, search=search,
            search_fields=["mrn", "first_name", "last_name", "phone"],
            sort_by=sort_by, sort_order=sort_order
        )

    def update_patient(self, db: Session, patient_id: str, patient_in: PatientUpdate) -> Patient:
        patient = self.get_patient(db, patient_id)
        return patient_repository.update(db, patient, patient_in.model_dump(exclude_unset=True))

    def delete_patient(self, db: Session, patient_id: str) -> bool:
        self.get_patient(db, patient_id)
        return patient_repository.delete(db, patient_id)

    # Ward, Room, Bed Management
    def create_ward(self, db: Session, ward_in: WardCreate) -> Ward:
        return ward_repository.create(db, ward_in.model_dump())

    def create_room(self, db: Session, room_in: RoomCreate) -> Room:
        return room_repository.create(db, room_in.model_dump())

    def create_bed(self, db: Session, bed_in: BedCreate) -> Bed:
        return bed_repository.create(db, bed_in.model_dump())

    def update_bed_status(self, db: Session, bed_id: str, status: BedStatusEnum) -> Bed:
        bed = bed_repository.get_by_id(db, bed_id)
        if not bed:
            raise NotFoundException(f"Bed with ID '{bed_id}' not found")
        return bed_repository.update(db, bed, {"status": status})

    # Emergency & Ambulance Management
    def create_emergency(self, db: Session, emergency_in: EmergencyCreate) -> Emergency:
        return emergency_repository.create(db, emergency_in.model_dump())

    def create_ambulance(self, db: Session, ambulance_in: AmbulanceCreate) -> Ambulance:
        return ambulance_repository.create(db, ambulance_in.model_dump())

patient_service = PatientService()
