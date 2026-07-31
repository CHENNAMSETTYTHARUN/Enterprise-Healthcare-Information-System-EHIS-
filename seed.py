import logging
from datetime import datetime, date, timedelta
from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.user import User, Role, Permission
from app.models.hospital import Hospital, Department, Doctor, Staff
from app.models.patient import Patient, Ward, Room, Bed, GenderEnum, BedStatusEnum
from app.models.lab_pharmacy import LabTest, Medicine, StockBatch
from app.models.billing import Invoice, InvoiceItem, InvoiceStatusEnum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ehis")

def seed_database():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        role_names = ["SUPER_ADMIN", "HOSPITAL_ADMIN", "DOCTOR", "NURSE", "PHARMACIST", "LAB_TECH", "ACCOUNTANT", "PATIENT"]
        roles_dict = {}
        for r_name in role_names:
            role = db.query(Role).filter(Role.name == r_name).first()
            if not role:
                role = Role(name=r_name, description=f"{r_name} role")
                db.add(role)
                db.flush()
            roles_dict[r_name] = role

        admin_email = "admin@ehis.com"
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash("Admin123!"),
                first_name="Super",
                last_name="Admin",
                phone_number="+18005550000",
                is_superuser=True,
                is_verified=True,
                roles=[roles_dict["SUPER_ADMIN"]]
            )
            db.add(admin_user)
            db.flush()

        hosp = db.query(Hospital).filter(Hospital.code == "HOSP-001").first()
        if not hosp:
            hosp = Hospital(
                name="St. Jude Memorial Hospital",
                code="HOSP-001",
                address="100 Healthcare Blvd, Medical City",
                phone="+18005551234",
                email="info@stjude.org"
            )
            db.add(hosp)
            db.flush()

        dept = db.query(Department).filter(Department.name == "Cardiology").first()
        if not dept:
            dept = Department(
                hospital_id=hosp.id,
                name="Cardiology",
                description="Cardiovascular medicine"
            )
            db.add(dept)
            db.flush()

        doc_email = "doctor.smith@ehis.com"
        doc_user = db.query(User).filter(User.email == doc_email).first()
        if not doc_user:
            doc_user = User(
                email=doc_email,
                hashed_password=get_password_hash("Doctor123!"),
                first_name="John",
                last_name="Smith",
                phone_number="+18005551111",
                is_verified=True,
                roles=[roles_dict["DOCTOR"]]
            )
            db.add(doc_user)
            db.flush()

            doctor = Doctor(
                user_id=doc_user.id,
                department_id=dept.id,
                specialization="Cardiologist",
                license_number="MD-998877",
                qualification="MD, FACC",
                consultation_fee="150.00"
            )
            db.add(doctor)
            db.flush()

        pat = db.query(Patient).filter(Patient.mrn == "MRN-100001").first()
        if not pat:
            pat = Patient(
                mrn="MRN-100001",
                first_name="Alice",
                last_name="Johnson",
                date_of_birth=date(1992, 4, 12),
                gender=GenderEnum.FEMALE,
                blood_group="O+",
                phone="+15559990001",
                address="456 Oak Avenue",
                medical_history="No known allergies"
            )
            db.add(pat)
            db.flush()

        ward = db.query(Ward).filter(Ward.name == "ICU Ward A").first()
        if not ward:
            ward = Ward(name="ICU Ward A", ward_type="ICU", floor="3rd Floor")
            db.add(ward)
            db.flush()

            room = Room(ward_id=ward.id, room_number="301", room_type="Deluxe ICU")
            db.add(room)
            db.flush()

            bed = Bed(room_id=room.id, bed_number="BED-01", status=BedStatusEnum.AVAILABLE)
            db.add(bed)
            db.flush()

        lab_test = db.query(LabTest).filter(LabTest.code == "CBC-001").first()
        if not lab_test:
            lab_test = LabTest(
                code="CBC-001",
                name="Complete Blood Count",
                category="Hematology",
                price=50.00,
                normal_range="WBC 4.5-11.0, RBC 4.3-5.9"
            )
            db.add(lab_test)
            db.flush()

        med = db.query(Medicine).filter(Medicine.code == "MED-AMX-500").first()
        if not med:
            med = Medicine(
                code="MED-AMX-500",
                name="Amoxicillin 500mg Capsule",
                generic_name="Amoxicillin",
                category="Antibiotics",
                unit_price=1.20
            )
            db.add(med)
            db.flush()

            batch = StockBatch(
                medicine_id=med.id,
                batch_number="BAT-2026-AMX",
                quantity=1000,
                expiry_date=date(2028, 12, 31)
            )
            db.add(batch)
            db.flush()

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Seeder error: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
