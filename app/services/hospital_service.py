from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.hospital import Hospital, Branch, Department, Doctor, Staff
from app.schemas.hospital import (
    HospitalCreate, BranchCreate, DepartmentCreate, DoctorCreate, StaffCreate
)
from app.core.exceptions import NotFoundException

hospital_repo = BaseRepository[Hospital](Hospital)
branch_repo = BaseRepository[Branch](Branch)
department_repo = BaseRepository[Department](Department)
doctor_repo = BaseRepository[Doctor](Doctor)
staff_repo = BaseRepository[Staff](Staff)

class HospitalService:
    def create_hospital(self, db: Session, h_in: HospitalCreate) -> Hospital:
        return hospital_repo.create(db, h_in.model_dump())

    def get_all_hospitals(self, db: Session, page: int, page_size: int, search: Optional[str]) -> Tuple[List[Hospital], int]:
        return hospital_repo.get_all(db, page=page, page_size=page_size, search=search, search_fields=["name", "code"])

    def create_branch(self, db: Session, b_in: BranchCreate) -> Branch:
        return branch_repo.create(db, b_in.model_dump())

    def create_department(self, db: Session, d_in: DepartmentCreate) -> Department:
        return department_repo.create(db, d_in.model_dump())

    def create_doctor(self, db: Session, doc_in: DoctorCreate) -> Doctor:
        return doctor_repo.create(db, doc_in.model_dump())

    def create_staff(self, db: Session, st_in: StaffCreate) -> Staff:
        return staff_repo.create(db, st_in.model_dump())

hospital_service = HospitalService()
