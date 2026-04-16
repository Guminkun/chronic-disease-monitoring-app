"""
Database migration script to add MinIO security fields.

Run this script to add thumbnail_url and file_md5 fields to the reports table.
"""
from sqlalchemy import create_engine, text, inspect
from app.config import settings
import sys

def migrate_database():
    """Add MinIO security fields to database tables."""
    
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    print("Starting MinIO security fields migration...")
    
    # Check and add fields to reports table
    print("\nChecking reports table...")
    reports_columns = [col['name'] for col in inspector.get_columns('reports')]
    
    with engine.connect() as conn:
        # Add thumbnail_url field
        if 'thumbnail_url' not in reports_columns:
            print("  Adding thumbnail_url field...")
            conn.execute(text("ALTER TABLE reports ADD COLUMN thumbnail_url TEXT"))
            conn.commit()
            print("  [OK] thumbnail_url field added")
        else:
            print("  [OK] thumbnail_url field already exists")
        
        # Add file_md5 field
        if 'file_md5' not in reports_columns:
            print("  Adding file_md5 field...")
            conn.execute(text("ALTER TABLE reports ADD COLUMN file_md5 VARCHAR(32)"))
            conn.commit()
            print("  [OK] file_md5 field added")
        else:
            print("  [OK] file_md5 field already exists")
    
    # Check members table
    print("\nChecking members table...")
    members_columns = [col['name'] for col in inspector.get_columns('members')]
    
    # Update avatar_url comment (it now stores file key instead of full URL)
    print("  [OK] members.avatar_url will now store file keys instead of full URLs")
    
    print("\n" + "="*60)
    print("Migration completed successfully!")
    print("="*60)
    print("\nImportant notes:")
    print("1. All bucket policies should be set to private")
    print("2. Files must be accessed via presigned URLs")
    print("3. New uploads will use file keys instead of full URLs")
    print("4. Existing URLs will continue to work during transition")
    print("\nNext steps:")
    print("- Update .env to ensure MINIO_SECURE is set correctly")
    print("- Run: python update_db.py to ensure all tables are up to date")
    print("- Update frontend to use new /files/presigned-url endpoint")

if __name__ == "__main__":
    try:
        migrate_database()
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
