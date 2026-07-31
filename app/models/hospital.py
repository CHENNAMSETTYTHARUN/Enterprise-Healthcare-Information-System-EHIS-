from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Hospital(BaseModel):
    __tablename__ = "hospitals"

    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    address = Column(String(255), nullable=True)
    phone = Column(String(30), nullable=True)
    email = Column(String(150), nullable=True)
    website = Column(String(150), nullable=True)

    branches = relationship("Branch", back_populates="hospital", cascade="all, delete-orphan")
    departments = relationship("Department", back_populates="hospital", cascade="all, delete-orphan")

class Branch(BaseModel):
    __tablename__ = "branches"

    hospital_id = Column(String(36), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=False)
    address = Column(String(255), nullable=True)
    phone = Column(String(30), nullable=True)

    hospital = relationship("Hospital", back_populates="branches")
    departments = relationship("Department", back_populates="branch")

class Department(BaseModel):
    __tablename__ = "departments"

    hospital_id = Column(String(36), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)
    branch_id = Column(String(36), ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=True)

    hospital = relationship("Hospital", back_populates="departments")
    branch = relationship("Branch", back_populates="departments")
    doctors = relationship("Doctor", back_populates="department")
    staff = relationship("Staff", back_populates="department")

class Doctor(BaseModel):
    __tablename__ = "doctors"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    department_id = Column(String(36), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    specialization = Column(String(150), nullable=False, index=True)
    license_number = Column(String(100), unique=True, nullable=False)
    qualification = Column(String(200), nullable=True)
    consultation_fee = Column(String(50), default="0.00")

    user = relationship("User", back_populates="doctor_profile")
    department = relationship("Department", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")
    opd_records = relationship("OPDRecord", back_populates="doctor")
    ipd_records = relationship("IPDRecord", back_populates="doctor")

class Staff(BaseModel):
    __tablename__ = "staff"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    department_id = Column(String(36), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    employee_id = Column(String(50), unique=True, nullable=False)
    designation = Column(String(100), nullable=False)

    user = relationship("User", back_populates="staff_profile")
    department = relationship("Department", back_populates="staff")
