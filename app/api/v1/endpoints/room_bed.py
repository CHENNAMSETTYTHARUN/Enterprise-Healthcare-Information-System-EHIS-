from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.rbac import require_roles
from app.services.patient_service import patient_service
from app.repositories.patient_repository import ward_repository, room_repository, bed_repository
from app.schemas.patient import WardCreate, WardResponse, RoomCreate, RoomResponse, BedCreate, BedResponse
from app.schemas.common import PaginatedResponse
from app.models.patient import BedStatusEnum

router = APIRouter(prefix="/facilities", tags=["Rooms & Beds Management"])

@router.post("/wards", response_model=WardResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN"]))])
def create_ward(ward_in: WardCreate, db: Session = Depends(get_db)):
    return patient_service.create_ward(db, ward_in)

@router.get("/wards", response_model=PaginatedResponse[WardResponse])
def get_wards(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    items, total = ward_repository.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)

@router.post("/rooms", response_model=RoomResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN"]))])
def create_room(room_in: RoomCreate, db: Session = Depends(get_db)):
    return patient_service.create_room(db, room_in)

@router.get("/rooms", response_model=PaginatedResponse[RoomResponse])
def get_rooms(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    items, total = room_repository.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)

@router.post("/beds", response_model=BedResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN", "NURSE"]))])
def create_bed(bed_in: BedCreate, db: Session = Depends(get_db)):
    return patient_service.create_bed(db, bed_in)

@router.get("/beds", response_model=PaginatedResponse[BedResponse])
def get_beds(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    items, total = bed_repository.get_all(db, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)

@router.put("/beds/{bed_id}/status", response_model=BedResponse, dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN", "NURSE"]))])
def update_bed_status(bed_id: str, status: BedStatusEnum, db: Session = Depends(get_db)):
    return patient_service.update_bed_status(db, bed_id, status)
