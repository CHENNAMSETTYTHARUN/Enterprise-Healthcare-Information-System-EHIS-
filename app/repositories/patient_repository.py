from typing import Optional
from sqlalchemy.orm import Session
from app.models.patient import Patient, Ward, Room, Bed, Emergency, Ambulance
from app.repositories.base import BaseRepository

class PatientRepository(BaseRepository[Patient]):
    def __init__(self):
        super().__init__(Patient)

    def get_by_mrn(self, db: Session, mrn: str) -> Optional[Patient]:
        return db.query(Patient).filter(Patient.mrn == mrn, Patient.is_active == True).first()

class WardRepository(BaseRepository[Ward]):
    def __init__(self):
        super().__init__(Ward)

class RoomRepository(BaseRepository[Room]):
    def __init__(self):
        super().__init__(Room)

class BedRepository(BaseRepository[Bed]):
    def __init__(self):
        super().__init__(Bed)

class EmergencyRepository(BaseRepository[Emergency]):
    def __init__(self):
        super().__init__(Emergency)

class AmbulanceRepository(BaseRepository[Ambulance]):
    def __init__(self):
        super().__init__(Ambulance)

patient_repository = PatientRepository()
ward_repository = WardRepository()
room_repository = RoomRepository()
bed_repository = BedRepository()
emergency_repository = EmergencyRepository()
ambulance_repository = AmbulanceRepository()
