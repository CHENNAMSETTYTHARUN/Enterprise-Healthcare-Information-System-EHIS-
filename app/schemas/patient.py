from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field
from app.models.patient import GenderEnum, BedStatusEnum, EmergencyStatusEnum

class PatientCreate(BaseModel):
    user_id: Optional[str] = None
    first_name: str = Field(..., example="Alice")
    last_name: str = Field(..., example="Johnson")
    date_of_birth: date = Field(..., example="1990-05-15")
    gender: GenderEnum = Field(..., example=GenderEnum.FEMALE)
    blood_group: Optional[str] = Field(None, example="O+")
    phone: Optional[str] = Field(None, example="+15550192834")
    emergency_contact: Optional[str] = Field(None, example="Bob Johnson (+15550192835)")
    address: Optional[str] = Field(None, example="456 Elm Street")
    medical_history: Optional[str] = Field(None, example="Asthma, Penicillin Allergy")

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    address: Optional[str] = None
    medical_history: Optional[str] = None

class PatientResponse(BaseModel):
    id: str
    mrn: str
    user_id: Optional[str] = None
    first_name: str
    last_name: str
    date_of_birth: date
    gender: GenderEnum
    blood_group: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    address: Optional[str] = None
    medical_history: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class WardCreate(BaseModel):
    name: str = Field(..., example="ICU Ward A")
    ward_type: str = Field(..., example="ICU")
    floor: Optional[str] = Field(None, example="3rd Floor")

class WardResponse(BaseModel):
    id: str
    name: str
    ward_type: str
    floor: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class RoomCreate(BaseModel):
    ward_id: str
    room_number: str = Field(..., example="301-A")
    room_type: str = Field(..., example="Deluxe Private")

class RoomResponse(BaseModel):
    id: str
    ward_id: str
    room_number: str
    room_type: str
    is_active: bool

    class Config:
        from_attributes = True

class BedCreate(BaseModel):
    room_id: str
    bed_number: str = Field(..., example="BED-01")
    status: BedStatusEnum = BedStatusEnum.AVAILABLE

class BedResponse(BaseModel):
    id: str
    room_id: str
    bed_number: str
    status: BedStatusEnum
    is_active: bool

    class Config:
        from_attributes = True

class EmergencyCreate(BaseModel):
    patient_id: str
    chief_complaint: str = Field(..., example="Severe chest pain and shortness of breath")
    triage_level: str = Field(..., example="RED")
    status: EmergencyStatusEnum = EmergencyStatusEnum.CRITICAL
    attending_doctor_id: Optional[str] = None

class EmergencyResponse(BaseModel):
    id: str
    patient_id: str
    chief_complaint: str
    triage_level: str
    status: EmergencyStatusEnum
    attending_doctor_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AmbulanceCreate(BaseModel):
    vehicle_number: str = Field(..., example="AMB-9901")
    driver_name: str = Field(..., example="Mark Davis")
    driver_phone: str = Field(..., example="+15558883333")
    is_available: bool = True

class AmbulanceResponse(BaseModel):
    id: str
    vehicle_number: str
    driver_name: str
    driver_phone: str
    is_available: bool

    class Config:
        from_attributes = True
