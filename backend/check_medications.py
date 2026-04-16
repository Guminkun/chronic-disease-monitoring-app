from app.database import SessionLocal
from app.models import Medication

db = SessionLocal()
try:
    count = db.query(Medication).count()
    print(f'Total medications: {count}')
    
    samples = db.query(Medication).limit(3).all()
    for m in samples:
        print(f'  - {m.generic_name} ({m.trade_name})')
finally:
    db.close()
