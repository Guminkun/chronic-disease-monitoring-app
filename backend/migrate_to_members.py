"""
数据迁移脚本：为现有数据关联成员ID
将所有现有数据关联到每个患者的"自己"成员
"""
from sqlalchemy import create_engine, text
from app.config import settings
import uuid

def migrate_data_to_members():
    print(f"Connecting to database: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # 1. 为每个患者创建"自己"成员（如果不存在）
        print("Step 1: Creating '自己' members for patients...")
        
        # 获取所有患者
        patients = conn.execute(text("SELECT id, name FROM patients")).fetchall()
        print(f"Found {len(patients)} patients")
        
        member_id_map = {}
        
        for patient_id, patient_name in patients:
            # 检查是否已有成员
            existing_member = conn.execute(
                text("SELECT id FROM members WHERE patient_id = :patient_id AND relation = '自己'"),
                {"patient_id": patient_id}
            ).first()
            
            if existing_member:
                member_id_map[patient_id] = existing_member[0]
                print(f"  Patient {patient_id} already has a '自己' member: {existing_member[0]}")
            else:
                # 创建"自己"成员
                member_id = str(uuid.uuid4())
                conn.execute(
                    text("""
                        INSERT INTO members (id, patient_id, nickname, relation, is_current, created_at, updated_at)
                        VALUES (:id, :patient_id, :nickname, '自己', TRUE, NOW(), NOW())
                    """),
                    {"id": member_id, "patient_id": patient_id, "nickname": patient_name or "本人"}
                )
                member_id_map[patient_id] = member_id
                print(f"  Created '自己' member for patient {patient_id}: {member_id}")
        
        conn.commit()
        print(f"Step 1 completed. Created/found {len(member_id_map)} members")
        
        # 2. 为所有现有数据关联 member_id
        print("\nStep 2: Associating existing data with '自己' members...")
        
        tables_to_update = [
            ("patient_diseases", "patient_id"),
            ("reports", "patient_id"),
            ("health_readings", "patient_id"),
            ("reminders", "patient_id"),
            ("revisit_plans", "patient_id"),
            ("revisit_records", "patient_id"),
            ("medication_plans", "patient_id")
        ]
        
        for table_name, patient_column in tables_to_update:
            try:
                # 检查表是否存在
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name} WHERE member_id IS NULL")).scalar()
                print(f"\n  Table {table_name}: {result} rows with NULL member_id")
                
                if result > 0:
                    # 更新 member_id
                    for patient_id, member_id in member_id_map.items():
                        update_result = conn.execute(
                            text(f"""
                                UPDATE {table_name}
                                SET member_id = :member_id
                                WHERE {patient_column} = :patient_id AND member_id IS NULL
                            """),
                            {"member_id": member_id, "patient_id": patient_id}
                        )
                        if update_result.rowcount > 0:
                            print(f"    Updated {update_result.rowcount} rows for patient {patient_id}")
                    
                    conn.commit()
                    print(f"  Table {table_name} updated successfully")
            except Exception as e:
                print(f"  Error updating table {table_name}: {e}")
        
        # 3. 验证数据迁移结果
        print("\nStep 3: Verifying migration results...")
        
        for table_name, patient_column in tables_to_update:
            try:
                null_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name} WHERE member_id IS NULL")).scalar()
                total_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                print(f"  {table_name}: {total_count} total, {null_count} with NULL member_id")
            except Exception as e:
                print(f"  Error checking table {table_name}: {e}")
        
        print("\nMigration completed successfully!")

if __name__ == "__main__":
    migrate_data_to_members()
