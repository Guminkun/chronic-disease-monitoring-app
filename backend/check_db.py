try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models import User, Patient
    from app.database import SQLALCHEMY_DATABASE_URL
    import sys

    if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
        )
    else:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    print("Users:")
    users = db.query(User).all()
    for u in users:
        print(f"ID: {u.id}, Phone: {u.phone}, Role: {u.role}")

    print("\nPatients:")
    patients = db.query(Patient).all()
    for p in patients:
        print(f"ID: {p.id}, Name: {p.name}, UserID: {p.user_id}")

    from app.models import Disease, PatientDisease
    print("\nDiseases (System Dictionary):")
    diseases = db.query(Disease).all()
    for d in diseases:
        print(f"ID: {d.id}, Name: {d.name}, Category: {d.category}")

    print("\nPatient Diseases (Patient Records):")
    p_diseases = db.query(PatientDisease).all()
    for pd in p_diseases:
        print(f"ID: {pd.id}, PatientID: {pd.patient_id}, Disease Name: {pd.name}, Status: {pd.status}")

    db.close()
except Exception as e:
    import traceback
    traceback.print_exc()
