from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class HospitalCreate(BaseModel):
    name: str = Field(..., example="St. Jude Memorial Hospital")
    code: str = Field(..., example="HOSP-001")
    address: Optional[str] = Field(None, example="123 Health Ave, Medical City")
    phone: Optional[str] = Field(None, example="+18005551234")
    email: Optional[str] = Field(None, example="contact@stjude.org")
    website: Optional[str] = Field(None, example="https://stjude.org")

class HospitalResponse(BaseModel):
    id: str
    name: str
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class BranchCreate(BaseModel):
    hospital_id: str
    name: str = Field(..., example="North Wing Branch")
    code: str = Field(..., example="BR-NORTH")
    address: Optional[str] = None
    phone: Optional[str] = None

class BranchResponse(BaseModel):
    id: str
    hospital_id: str
    name: str
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class DepartmentCreate(BaseModel):
    hospital_id: str
    branch_id: Optional[str] = None
    name: str = Field(..., example="Cardiology")
    description: Optional[str] = Field(None, example="Cardiovascular research and treatment")

class DepartmentResponse(BaseModel):
    id: str
    hospital_id: str
    branch_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class DoctorCreate(BaseModel):
    user_id: str
    department_id: Optional[str] = None
    specialization: str = Field(..., example="Cardiologist")
    license_number: str = Field(..., example="MD-987654")
    qualification: Optional[str] = Field(None, example="MD, FACC")
    consultation_fee: str = Field("150.00", example="150.00")

class DoctorResponse(BaseModel):
    id: str
    user_id: str
    department_id: Optional[str] = None
    specialization: str
    license_number: str
    qualification: Optional[str] = None
    consultation_fee: str
    is_active: bool

    class Config:
        from_attributes = True

class StaffCreate(BaseModel):
    user_id: str
    department_id: Optional[str] = None
    employee_id: str = Field(..., example="EMP-1001")
    designation: str = Field(..., example="Head Nurse")

class StaffResponse(BaseModel):
    id: str
    user_id: str
    department_id: Optional[str] = None
    employee_id: str
    designation: str
    is_active: bool

    class Config:
        from_attributes = True
