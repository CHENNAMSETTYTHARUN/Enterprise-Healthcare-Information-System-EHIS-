from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.patient import Patient
from app.models.hospital import Doctor, Department, Hospital
from app.models.user import User
from app.models.lab_pharmacy import Medicine, LabTest

class SearchService:
    def search_all(self, db: Session, query: str, limit: int = 20):
        q = f"%{query}%"

        patients = db.query(Patient).filter(
            or_(
                Patient.first_name.ilike(q),
                Patient.last_name.ilike(q),
                Patient.mrn.ilike(q),
                Patient.phone.ilike(q)
            )
        ).limit(limit).all()

        doctors = db.query(Doctor).join(User, Doctor.user_id == User.id).filter(
            or_(
                User.first_name.ilike(q),
                User.last_name.ilike(q),
                Doctor.specialization.ilike(q),
                Doctor.license_number.ilike(q)
            )
        ).limit(limit).all()

        medicines = db.query(Medicine).filter(
            or_(
                Medicine.name.ilike(q),
                Medicine.generic_name.ilike(q),
                Medicine.code.ilike(q)
            )
        ).limit(limit).all()

        lab_tests = db.query(LabTest).filter(
            or_(
                LabTest.name.ilike(q),
                LabTest.code.ilike(q),
                LabTest.category.ilike(q)
            )
        ).limit(limit).all()

        departments = db.query(Department).filter(
            Department.name.ilike(q)
        ).limit(limit).all()

        return {
            "query": query,
            "results": {
                "patients": [{"id": p.id, "name": f"{p.first_name} {p.last_name}", "mrn": p.mrn} for p in patients],
                "doctors": [{"id": d.id, "specialization": d.specialization, "license_number": d.license_number} for d in doctors],
                "medicines": [{"id": m.id, "name": m.name, "generic_name": m.generic_name, "code": m.code} for m in medicines],
                "lab_tests": [{"id": lt.id, "name": lt.name, "code": lt.code, "category": lt.category} for lt in lab_tests],
                "departments": [{"id": d.id, "name": d.name} for d in departments]
            },
            "total": len(patients) + len(doctors) + len(medicines) + len(lab_tests) + len(departments)
        }

    def search_patients(self, db: Session, query: str, limit: int = 50):
        q = f"%{query}%"
        patients = db.query(Patient).filter(
            or_(
                Patient.first_name.ilike(q),
                Patient.last_name.ilike(q),
                Patient.mrn.ilike(q),
                Patient.phone.ilike(q)
            )
        ).limit(limit).all()
        return [{"id": p.id, "name": f"{p.first_name} {p.last_name}", "mrn": p.mrn, "phone": p.phone, "gender": p.gender} for p in patients]

    def search_medicines(self, db: Session, query: str, limit: int = 50):
        q = f"%{query}%"
        medicines = db.query(Medicine).filter(
            or_(
                Medicine.name.ilike(q),
                Medicine.generic_name.ilike(q),
                Medicine.code.ilike(q),
                Medicine.category.ilike(q)
            )
        ).limit(limit).all()
        return [{"id": m.id, "name": m.name, "generic_name": m.generic_name, "code": m.code, "category": m.category, "unit_price": float(m.unit_price)} for m in medicines]

search_service = SearchService()
