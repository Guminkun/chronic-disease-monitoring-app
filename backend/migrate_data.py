import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, make_transient
from app.models import Base, User, Patient, Doctor, Disease, PatientDisease, Report, DoctorPatientBinding, ClinicalNote, HealthReading, SystemLog, Indicator, DiseaseIndicator
from app.database import SessionLocal as PgSessionLocal, engine as pg_engine

# SQLite setup
SQLITE_URL = "sqlite:///./sql_app.db"
sqlite_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SqliteSession = sessionmaker(bind=sqlite_engine)

def migrate():
    if not os.path.exists("./sql_app.db"):
        print("Error: sql_app.db not found!")
        return

    sqlite_db = SqliteSession()
    pg_db = PgSessionLocal()
    
    try:
        print("Starting migration...")
        
        # Clean Postgres tables first to avoid conflicts
        print("Cleaning existing data in Postgres...")
        # Drop tables to ensure schema consistency
        pg_db.execute(text("DROP TABLE IF EXISTS system_logs, health_readings, clinical_notes, doctor_patient_bindings, reports, disease_indicators, patient_diseases, indicators, diseases, doctors, patients, users, admins CASCADE"))
        pg_db.commit()
        print("Dropped existing tables.")
        
        # Recreate tables
        print("Recreating tables...")
        Base.metadata.create_all(bind=pg_engine)
        print("Tables recreated.")

        # Helper to migrate a table
        def migrate_table(model, name):
            print(f"Migrating {name}...")
            records = sqlite_db.query(model).all()
            count = 0
            for record in records:
                # Check if exists in PG (by ID)
                # For composite PKs or different ID types, we might need adjustments
                # But for simple migration into empty DB, we can skip check or check generically
                # Since we dropped tables, we can just add.
                
                # Detach from SQLite session
                sqlite_db.expunge(record)
                make_transient(record)
                pg_db.add(record)
                count += 1
            pg_db.commit()
            print(f"Migrated {count} {name}.")

        # 1. Users
        migrate_table(User, "Users")
        
        # 2. Patients
        migrate_table(Patient, "Patients")

        # 3. Doctors
        migrate_table(Doctor, "Doctors")
        
        # 4. Diseases
        migrate_table(Disease, "Diseases")
        
        # 5. Indicators
        migrate_table(Indicator, "Indicators")

        # 6. DiseaseIndicators
        migrate_table(DiseaseIndicator, "DiseaseIndicators")

        # 7. PatientDiseases
        migrate_table(PatientDisease, "PatientDiseases")
        
        # 8. Reports
        migrate_table(Report, "Reports")
        
        # 9. DoctorPatientBinding
        migrate_table(DoctorPatientBinding, "DoctorPatientBindings")
        
        # 10. ClinicalNote
        migrate_table(ClinicalNote, "ClinicalNotes")
        
        # 11. HealthReading
        migrate_table(HealthReading, "HealthReadings")
        
        # 12. SystemLog
        migrate_table(SystemLog, "SystemLogs")
        
        # Update sequences for Integer PK tables
        print("Updating sequences...")
        for table in ["diseases", "patient_diseases", "indicators"]:
            try:
                seq_name = f"{table}_id_seq"
                pg_db.execute(text(f"SELECT setval('{seq_name}', COALESCE((SELECT MAX(id) FROM {table}), 0) + 1, false)"))
            except Exception as e:
                print(f"Sequence update failed for {table}: {e}")
        pg_db.commit()

        print("Migration completed successfully!")

    except Exception as e:
        print(f"Migration failed: {e}")
        pg_db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        sqlite_db.close()
        pg_db.close()

if __name__ == "__main__":
    migrate()
