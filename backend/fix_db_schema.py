from sqlalchemy import create_engine, text
import os

# 从环境变量或直接硬编码测试 (根据 .env)
DATABASE_URL = "postgresql://test:Psbc%401234@192.168.88.205:5432/testdb"

def check_columns():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # 检查 medications 表的列
            query = text("SELECT column_name FROM information_schema.columns WHERE table_name = 'medications'")
            result = conn.execute(query).fetchall()
            columns = [row[0] for row in result]
            print(f"Current columns in 'medications': {columns}")
            
            required_columns = ['usage_dosage', 'side_effects']
            missing = [col for col in required_columns if col not in columns]
            
            if missing:
                print(f"Missing columns: {missing}")
                # 尝试自动添加缺失列 (仅用于开发环境快速修复)
                for col in missing:
                    print(f"Adding column: {col}")
                    alter_query = text(f"ALTER TABLE medications ADD COLUMN {col} TEXT")
                    conn.execute(alter_query)
                    conn.commit()
                print("Columns added successfully.")
            else:
                print("All required columns exist.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_columns()
