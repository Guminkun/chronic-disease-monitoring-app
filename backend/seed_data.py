
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, Admin, Doctor, Patient, UserRole, DoctorStatus, GenderType
from app.database import SQLALCHEMY_DATABASE_URL
from app.auth_utils import get_password_hash
import uuid

# Setup DB connection
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def seed():
    print("Seeding database...")

    # 1. Create Admin
    admin_phone = "admin"
    if not db.query(User).filter(User.phone == admin_phone).first():
        print("Creating admin user...")
        admin_user = User(
            id=uuid.uuid4(),
            phone=admin_phone,
            password_hash=get_password_hash("admin"),
            role=UserRole.admin,
            is_active=True
        )
        db.add(admin_user)
        db.flush() # flush to get ID

        admin_profile = Admin(
            id=uuid.uuid4(),
            user_id=admin_user.id,
            name="System Admin",
            role_level="super_admin"
        )
        db.add(admin_profile)
        print("Admin created.")

    # 2. Create Doctor
    doctor_phone = "13900000001"
    if not db.query(User).filter(User.phone == doctor_phone).first():
        print("Creating doctor user...")
        doctor_user = User(
            id=uuid.uuid4(),
            phone=doctor_phone,
            password_hash=get_password_hash("123456"),
            role=UserRole.doctor,
            is_active=True
        )
        db.add(doctor_user)
        db.flush()

        doctor_profile = Doctor(
            id=uuid.uuid4(),
            user_id=doctor_user.id,
            name="王医生",
            department="心血管内科",
            hospital="第一人民医院",
            specialties=["高血压", "冠心病"],
            status=DoctorStatus.approved
        )
        db.add(doctor_profile)
        print("Doctor created.")

    # 3. Create Patient
    patient_phone = "13800000001"
    if not db.query(User).filter(User.phone == patient_phone).first():
        print("Creating patient user...")
        patient_user = User(
            id=uuid.uuid4(),
            phone=patient_phone,
            password_hash=get_password_hash("123456"),
            role=UserRole.patient,
            is_active=True
        )
        db.add(patient_user)
        db.flush()

        patient_profile = Patient(
            id=uuid.uuid4(),
            user_id=patient_user.id,
            name="张三",
            gender=GenderType.male,
            age=45,
            id_card="110101198001011234",
            medical_history="高血压2年",
            allergies="无"
        )
        db.add(patient_profile)
        print("Patient created.")

    try:
        db.commit()
        print("Seeding completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
