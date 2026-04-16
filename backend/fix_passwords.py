from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.auth_utils import get_password_hash
from app.models import User

def fix_passwords():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Define the common password hash for "123456"
        common_password = "123456"
        common_hash = get_password_hash(common_password)
        
        # Define the admin password hash for "admin"
        admin_password = "admin"
        admin_hash = get_password_hash(admin_password)

        print(f"Updating passwords...")

        # Update specific users
        users_to_update = [
            {"phone": "13800000001", "hash": common_hash},
            {"phone": "13900000001", "hash": common_hash},
            {"phone": "admin", "hash": admin_hash}
        ]

        for u in users_to_update:
            user = db.query(User).filter(User.phone == u["phone"]).first()
            if user:
                user.password_hash = u["hash"]
                print(f"Updated password for user {u['phone']}")
            else:
                print(f"User {u['phone']} not found")
        
        db.commit()
        print("Password update complete.")
        
    except Exception as e:
        print(f"Error updating passwords: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_passwords()
