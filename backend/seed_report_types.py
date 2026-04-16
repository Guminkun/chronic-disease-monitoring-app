import os
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models

def seed_report_types():
    db = SessionLocal()
    
    # Check if table is empty
    if db.query(models.ReportType).count() > 0:
        print("ReportType table already has data. Clearing it...")
        db.query(models.ReportType).delete()
        db.commit()

    file_path = r"C:\Users\郭帅\Desktop\chronic-disease-monitoring-app\字典.txt"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    current_category = None
    count = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            # Check for category (e.g., "一、 实验室检查")
            # Using simple heuristic: starts with Chinese number + "、"
            chinese_nums = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
            is_category = False
            for num in chinese_nums:
                if line.startswith(f"{num}、"):
                    is_category = True
                    # Extract category name (remove "一、 ")
                    current_category = line.split("、", 1)[1].strip()
                    break
            
            if is_category:
                continue
                
            # It's a report type item
            if current_category:
                report_type = models.ReportType(
                    category=current_category,
                    name=line
                )
                db.add(report_type)
                count += 1
    
    db.commit()
    print(f"Successfully seeded {count} report types.")
    db.close()

if __name__ == "__main__":
    # Ensure tables exist
    models.Base.metadata.create_all(bind=engine)
    seed_report_types()
