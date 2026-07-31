from sqlalchemy import Column, String, Date, Text, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel

class GenderEnum(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class BedStatusEnum(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    MAINTENANCE = "MAINTENANCE"

class EmergencyStatusEnum(str, enum.Enum):
    CRITICAL = "CRITICAL"
    STABLE = "STABLE"
    DISCHARGED = "DISCHARGED"
    TRANSFERRED = "TRANSFERRED"

class Patient(BaseModel):
    __tablename__ = "patients"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True)
    mrn = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    blood_group = Column(String(10), nullable=True)
    phone = Column(String(30), nullable=True)
    emergency_contact = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    medical_history = Column(Text, nullable=True)

    user = relationship("User", back_populates="patient_profile")
    appointments = relationship("Appointment", back_populates="patient")
    opd_records = relationship("OPDRecord", back_populates="patient")
    ipd_records = relationship("IPDRecord", back_populates="patient")
    emr_records = relationship("EMRRecord", back_populates="patient")
    lab_orders = relationship("LabOrder", back_populates="patient")
    invoices = relationship("Invoice", back_populates="patient")

class Ward(BaseModel):
    __tablename__ = "wards"

    name = Column(String(100), nullable=False)
    ward_type = Column(String(50), nullable=False)
    floor = Column(String(20), nullable=True)

    rooms = relationship("Room", back_populates="ward", cascade="all, delete-orphan")

class Room(BaseModel):
    __tablename__ = "rooms"

    ward_id = Column(String(36), ForeignKey("wards.id", ondelete="CASCADE"), nullable=False)
    room_number = Column(String(30), nullable=False)
    room_type = Column(String(50), nullable=False)

    ward = relationship("Ward", back_populates="rooms")
    beds = relationship("Bed", back_populates="room", cascade="all, delete-orphan")

class Bed(BaseModel):
    __tablename__ = "beds"

    room_id = Column(String(36), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    bed_number = Column(String(30), nullable=False)
    status = Column(Enum(BedStatusEnum), default=BedStatusEnum.AVAILABLE, nullable=False)

    room = relationship("Room", back_populates="beds")
    ipd_records = relationship("IPDRecord", back_populates="bed")

class Emergency(BaseModel):
    __tablename__ = "emergencies"

    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    chief_complaint = Column(Text, nullable=False)
    triage_level = Column(String(30), nullable=False)
    status = Column(Enum(EmergencyStatusEnum), default=EmergencyStatusEnum.CRITICAL, nullable=False)
    attending_doctor_id = Column(String(36), ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True)

class Ambulance(BaseModel):
    __tablename__ = "ambulances"

    vehicle_number = Column(String(50), unique=True, nullable=False)
    driver_name = Column(String(100), nullable=False)
    driver_phone = Column(String(30), nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
