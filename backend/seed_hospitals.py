import csv
import sys
import os

# Add backend directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app import models

def seed_hospitals():
    db = SessionLocal()
    
    # Ensure table exists
    models.Base.metadata.create_all(bind=engine)
    
    csv_path = r"C:\Users\郭帅\Desktop\chronic-disease-monitoring-app\医院.csv"
    
    if not os.path.exists(csv_path):
        print(f"Error: File not found at {csv_path}")
        return

    print("Starting to seed hospitals...")
    count = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Map CSV columns to model fields
                hospital = models.Hospital(
                    name=row.get('医院名称', '').strip(),
                    alias=row.get('医院别名', '').strip(),
                    level=row.get('医院等级', '').strip(),
                    type=row.get('医院类型', '').strip(),
                    address=row.get('医院地址', '').strip(),
                    phone=row.get('电话', '').strip(),
                    province=row.get('省', '').strip(),
                    city=row.get('市', '').strip(),
                    district=row.get('区县', '').strip(),
                    website=row.get('医院网址', '').strip()
                )
                
                # Check if already exists (by name)
                existing = db.query(models.Hospital).filter(models.Hospital.name == hospital.name).first()
                if not existing:
                    db.add(hospital)
                    count += 1
                else:
                    # Optional: Update existing record
                    pass
            
            db.commit()
            print(f"Successfully added {count} hospitals.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_hospitals()
