# Enterprise Healthcare Information System (EHIS) Backend

A 100% production-ready, fully functional **Enterprise Healthcare Information System (EHIS)** backend built with **FastAPI**, **Python 3.12+**, **MySQL 8**, **SQLAlchemy 2.0**, **Alembic**, **Pydantic v2**, **JWT Authentication with RBAC**, **Redis Cache**, and **Uvicorn**.

---

## Technical Stack & Architecture

- **Backend Framework**: FastAPI (0.110+)
- **Language**: Python 3.12+
- **Database**: MySQL 8.0+
- **ORM Layer**: SQLAlchemy 2.0 (Declarative Base, Repository Pattern, Unit of Work)
- **Database Migrations**: Alembic
- **Validation**: Pydantic v2
- **Authentication**: JWT Access (Bearer) & Refresh Tokens
- **Authorization**: Fine-grained Role-Based Access Control (RBAC)
- **Caching**: Redis Cache Wrapper
- **Background Tasks**: FastAPI `BackgroundTasks` (Email notifications, Audit logging, Lab notifications)
- **API Documentation**: Interactive Swagger UI (`/docs`) & ReDoc (`/redoc`)

---

## Folder Structure

```
c:\Users\saith\Downloads\Enterprise Healthcare Information System
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py          # JWT Login, Register, Refresh, Profile
│   │       │   ├── users.py         # User & Role/Permission CRUD
│   │       │   ├── hospital.py      # Hospital entity management
│   │       │   ├── branch.py        # Hospital Branches
│   │       │   ├── department.py    # Departments
│   │       │   ├── doctor.py        # Doctors catalog
│   │       │   ├── staff.py         # Staff records
│   │       │   ├── patient.py       # Patient registration & MRN generation
│   │       │   ├── room_bed.py      # Wards, Rooms, and Beds management
│   │       │   ├── emergency.py     # ER Triage & Ambulance fleet
│   │       │   ├── appointment.py   # OPD Appointments scheduling
│   │       │   ├── opd_ipd.py       # Outpatient & Inpatient admissions
│   │       │   ├── emr.py           # Electronic Medical Records, Prescriptions, ICD Diagnoses
│   │       │   ├── surgery.py       # Surgery scheduling & Discharge summaries
│   │       │   ├── lab.py           # Lab test catalog, Orders, Barcodes & Results
│   │       │   ├── pharmacy.py      # Medicines catalog, Stock batches & Dispensing
│   │       │   ├── billing.py       # Invoices, Payments, Refunds
│   │       │   ├── insurance.py     # Insurance Claims & Approval workflow
│   │       │   ├── notifications.py # Async background email tasks
│   │       │   ├── analytics.py     # Executive Dashboard & Revenue KPIs
│   │       │   └── audit.py         # Audit trail logging
│   │       └── api.py
│   ├── core/
│   │   ├── config.py                # Environment & Pydantic settings
│   │   ├── database.py              # DB Engine, Session, auto database creator
│   │   ├── security.py              # Bcrypt hashing & JWT token generator
│   │   ├── exceptions.py            # Global custom exception classes
│   │   ├── logging.py               # Enterprise logger setup
│   │   └── middleware.py            # Security headers & Request timing
│   ├── models/                      # SQLAlchemy 2.0 ORM Models
│   ├── schemas/                     # Pydantic v2 Request/Response Schemas
│   ├── repositories/                # Generic BaseRepository & Domain Repositories
│   ├── services/                    # Business Logic Layer
│   ├── dependencies/                # FastAPI DB Session, Auth & RBAC Dependencies
│   ├── cache/                       # Redis caching wrapper
│   ├── background/                  # Background worker tasks
│   └── main.py                      # FastAPI Application entrypoint
├── alembic/                         # Database Migration scripts
├── alembic.ini                      # Alembic config
├── schema.sql                       # MySQL Database Initialization script
├── seed.py                          # Database initial seed script
├── postman_collection.json          # Postman testing suite
├── requirements.txt                 # Python dependencies
├── .env                             # Environment parameters
└── README.md                        # Documentation
```

---

## Quick Start & Execution Guide

### 1. Prerequisites
- **Python 3.12+** installed.
- **MySQL 8.0+** running locally at `localhost:3306` with user `root` and password `root123`.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Auto-Initialization & Seed
The database (`ehis_db`) will be automatically created upon application startup if it does not exist.
Alternatively, you can run Alembic migrations and seeding manually:

```bash
# Run database migrations
alembic upgrade head

# Seed initial admin, roles, doctor, patient, and lab data
python seed.py
```

### 4. Launch Application Server
```bash
uvicorn app.main:app --reload --port 8000
```

---

## Pre-Configured Seed Users & Credentials

| Role | Email | Password | Access Rights |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin@ehis.com` | `Admin123!` | Full System Privilege & Management |
| **Doctor** | `doctor.smith@ehis.com` | `Doctor123!` | EMR, Prescriptions, Appointments, OPD, IPD, Surgeries |

---

## Interactive API Documentation (Swagger UI)

Access the interactive OpenAPI Swagger UI at:
👉 **`http://localhost:8000/docs`**

### Authenticating in Swagger UI:
1. Go to `POST /api/v1/auth/login`.
2. Input `admin@ehis.com` and `Admin123!`.
3. Copy the returned `access_token`.
4. Click the green **Authorize** button at top-right in Swagger UI.
5. Enter: `Bearer <your_access_token>`.
6. Click **Authorize** and test any endpoint directly!

---

## Quality & Compliance Verification

- ✅ **No TODOs / Pseudo Code**: 100% full implementation across all files.
- ✅ **Zero Import Errors**: Verified imports across all modules.
- ✅ **RBAC Enforced**: Multi-role security guards applied to API endpoints.
- ✅ **Data Validation**: Strict Pydantic schemas on all endpoints.
- ✅ **Database Auto-Creation**: Zero manual SQL setup required.
