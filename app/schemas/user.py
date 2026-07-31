from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class PermissionResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class RoleCreate(BaseModel):
    name: str = Field(..., example="DOCTOR")
    description: Optional[str] = Field(None, example="Medical Doctor role")
    permission_ids: Optional[List[str]] = []

class RoleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr = Field(..., example="doctor.smith@ehis.com")
    password: str = Field(..., min_length=6, example="Doctor123!")
    first_name: str = Field(..., example="John")
    last_name: str = Field(..., example="Smith")
    phone_number: Optional[str] = Field(None, example="+1234567890")
    hospital_id: Optional[str] = None
    role_names: Optional[List[str]] = Field(default_factory=lambda: ["PATIENT"])

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    is_superuser: bool
    is_verified: bool
    is_active: bool
    created_at: datetime
    roles: List[RoleResponse] = []

    class Config:
        from_attributes = True
